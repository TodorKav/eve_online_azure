import json
from django.test import TestCase, Client
from django.urls import reverse
from eve.accounts.models import CustomUser
from eve.watchlist.models import Watchlist, WatchlistItem
from eve.industry.models import Types, CorporationsWithLPStores


class WatchlistTestBase(TestCase):

    def setUp(self):
        self.client = Client()

        self.user = CustomUser.objects.create_user(username="testuser", password="pass")
        self.other_user = CustomUser.objects.create_user(username="otheruser", password="pass")

        self.item = Types.objects.create(
            type_id=1,
            name="Tritanium",
            description="A test item",
        )

        self.corporation = CorporationsWithLPStores.objects.create(
            corporation_id=1,
            name="Test Corp",
            description="A test corporation",
            ticker="TEST",
        )

        self.unsorted, _ = Watchlist.objects.get_or_create(user=self.user, name="Unsorted")
        self.watchlist, _ = Watchlist.objects.get_or_create(user=self.user, name="My List")

        self.watchlist_item, _ = WatchlistItem.objects.get_or_create(
            watchlist=self.unsorted,
            item=self.item,
            corporation=self.corporation,
        )

        self.client.login(username="testuser", password="pass")




class WatchlistViewTest(WatchlistTestBase):

    def test_redirects_if_not_logged_in(self):
        self.client.logout()
        response = self.client.get(reverse('watchlist:watchlist'))
        self.assertNotEqual(response.status_code, 200)

    def test_returns_200_for_logged_in_user(self):
        response = self.client.get(reverse('watchlist:watchlist'))
        self.assertEqual(response.status_code, 200)

    def test_only_returns_current_users_watchlists(self):
        Watchlist.objects.create(user=self.other_user, name="Other List")
        response = self.client.get(reverse('watchlist:watchlist'))
        for watchlist in response.context['object_list']:
            self.assertEqual(watchlist.user, self.user)

    def test_does_not_return_other_users_watchlists(self):
        other_wl = Watchlist.objects.create(user=self.other_user, name="Other List")
        response = self.client.get(reverse('watchlist:watchlist'))
        ids = [wl.pk for wl in response.context['object_list']]
        self.assertNotIn(other_wl.pk, ids)



class AddItemsViewTest(WatchlistTestBase):

    def _post(self, items):
        return self.client.post(
            reverse('watchlist:watchlist-items-save'),
            {'selected_items': [json.dumps(i) for i in items]},
        )

    def test_redirects_if_not_logged_in(self):
        self.client.logout()
        response = self._post([])
        self.assertNotEqual(response.status_code, 200)

    def test_redirects_to_watchlist_on_success(self):
        response = self._post([{'type_id': self.item.pk, 'corporation_id': self.corporation.pk}])
        self.assertRedirects(response, reverse('watchlist:watchlist'))

    def test_creates_watchlist_items(self):
        new_item = Types.objects.create(type_id=2, name="Pyerite")
        initial_count = WatchlistItem.objects.count()
        self._post([{'type_id': new_item.pk, 'corporation_id': self.corporation.pk}])
        self.assertEqual(WatchlistItem.objects.count(), initial_count + 1)

    def test_renders_error_when_unsorted_watchlist_missing(self):
        self.unsorted.delete()
        response = self._post([{'type_id': self.item.pk, 'corporation_id': self.corporation.pk}])
        self.assertTemplateUsed(response, 'watchlist/signal_error.html')

    def test_duplicate_item_does_not_raise(self):
        """bulk_create with update_conflicts should not raise on duplicates."""
        payload = [{'type_id': self.item.pk, 'corporation_id': self.corporation.pk}]
        self._post(payload)
        try:
            self._post(payload)
        except Exception as e:
            self.fail(f"Duplicate item raised an exception: {e}")

    def test_get_request_redirects(self):
        response = self.client.get(reverse('watchlist:watchlist-items-save'))
        self.assertRedirects(response, reverse('watchlist:watchlist'))



class AddTableViewTest(WatchlistTestBase):

    def test_get_returns_200(self):
        response = self.client.get(reverse('watchlist:add-table'))
        self.assertEqual(response.status_code, 200)

    def test_creates_watchlist_assigned_to_current_user(self):
        self.client.post(reverse('watchlist:add-table'), {'name': 'New List'})
        self.assertTrue(Watchlist.objects.filter(user=self.user, name='New List').exists())

    def test_redirects_on_success(self):
        response = self.client.post(reverse('watchlist:add-table'), {'name': 'New List'})
        self.assertRedirects(response, reverse('watchlist:watchlist'))

    def test_cannot_create_duplicate_name_for_same_user(self):
        response = self.client.post(reverse('watchlist:add-table'), {'name': 'My List'})
        # Should not create a second one — form invalid or DB error
        count = Watchlist.objects.filter(user=self.user, name='My List').count()
        self.assertEqual(count, 1)

    def test_redirects_if_not_logged_in(self):
        self.client.logout()
        response = self.client.post(reverse('watchlist:add-table'), {'name': 'X'})
        self.assertNotEqual(response.status_code, 200)



class EditTableViewTest(WatchlistTestBase):

    def test_get_returns_200(self):
        response = self.client.get(reverse('watchlist:edit-table', kwargs={'pk': self.watchlist.pk}))
        self.assertEqual(response.status_code, 200)

    def test_updates_watchlist_name(self):
        self.client.post(
            reverse('watchlist:edit-table', kwargs={'pk': self.watchlist.pk}),
            {'name': 'Renamed List'}
        )
        self.watchlist.refresh_from_db()
        self.assertEqual(self.watchlist.name, 'Renamed List')

    def test_redirects_on_success(self):
        response = self.client.post(
            reverse('watchlist:edit-table', kwargs={'pk': self.watchlist.pk}),
            {'name': 'Renamed List'}
        )
        self.assertRedirects(response, reverse('watchlist:watchlist'))


class DeleteTableViewTest(WatchlistTestBase):

    def test_get_returns_200(self):
        response = self.client.get(reverse('watchlist:delete-table', kwargs={'pk': self.watchlist.pk}))
        self.assertEqual(response.status_code, 200)

    def test_deletes_non_unsorted_watchlist(self):
        self.client.post(reverse('watchlist:delete-table', kwargs={'pk': self.watchlist.pk}))
        self.assertFalse(Watchlist.objects.filter(pk=self.watchlist.pk).exists())

    def test_does_not_delete_unsorted_watchlist(self):
        self.client.post(reverse('watchlist:delete-table', kwargs={'pk': self.unsorted.pk}))
        self.assertTrue(Watchlist.objects.filter(pk=self.unsorted.pk).exists())

    def test_redirects_after_delete(self):
        response = self.client.post(reverse('watchlist:delete-table', kwargs={'pk': self.watchlist.pk}))
        self.assertRedirects(response, reverse('watchlist:watchlist'))

    def test_redirects_even_when_unsorted_blocked(self):
        response = self.client.post(reverse('watchlist:delete-table', kwargs={'pk': self.unsorted.pk}))
        self.assertRedirects(response, reverse('watchlist:watchlist'))


class MoveItemsViewTest(WatchlistTestBase):

    def _move_post(self, move_ids, target_watchlist_data):
        return self.client.post(
            reverse('watchlist:move-items'),
            {
                'move': move_ids,
                'target_watchlist': [json.dumps(d) for d in target_watchlist_data],
            }
        )

    def test_moves_item_to_target_watchlist(self):
        self._move_post(
            move_ids=[self.watchlist_item.pk],
            target_watchlist_data=[{
                'watchlist_item_entry': self.watchlist_item.pk,
                'current_watchlist': self.unsorted.pk,
                'target_watchlist': self.watchlist.pk,
                'type_id': self.item.pk,
                'corporation_id': self.corporation.pk,
            }]
        )
        self.assertTrue(
            WatchlistItem.objects.filter(watchlist=self.watchlist, item=self.item).exists()
        )
        self.assertFalse(
            WatchlistItem.objects.filter(watchlist=self.unsorted, item=self.item).exists()
        )

    def test_no_move_ids_redirects_immediately(self):
        response = self._move_post(move_ids=[], target_watchlist_data=[])
        self.assertRedirects(response, reverse('watchlist:watchlist'))

    def test_does_not_move_if_same_watchlist(self):
        """Moving to the same watchlist should be a no-op."""
        initial_count = WatchlistItem.objects.count()
        self._move_post(
            move_ids=[self.watchlist_item.pk],
            target_watchlist_data=[{
                'watchlist_item_entry': self.watchlist_item.pk,
                'current_watchlist': self.unsorted.pk,
                'target_watchlist': self.unsorted.pk,
                'type_id': self.item.pk,
                'corporation_id': self.corporation.pk,
            }]
        )
        self.assertEqual(WatchlistItem.objects.count(), initial_count)

    def test_redirects_on_success(self):
        response = self._move_post(
            move_ids=[self.watchlist_item.pk],
            target_watchlist_data=[{
                'watchlist_item_entry': self.watchlist_item.pk,
                'current_watchlist': self.unsorted.pk,
                'target_watchlist': self.watchlist.pk,
                'type_id': self.item.pk,
                'corporation_id': self.corporation.pk,
            }]
        )
        self.assertRedirects(response, reverse('watchlist:watchlist'))


class WatchlistDescriptionEditViewTest(WatchlistTestBase):

    def test_get_returns_200(self):
        response = self.client.get(
            reverse('watchlist:edit-description', kwargs={'pk': self.watchlist.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_updates_description(self):
        self.client.post(
            reverse('watchlist:edit-description', kwargs={'pk': self.watchlist.pk}),
            {'description': 'My new description'}
        )
        self.watchlist.refresh_from_db()
        self.assertEqual(self.watchlist.description, 'My new description')

    def test_other_user_cannot_edit(self):
        self.client.login(username='otheruser', password='pass')
        response = self.client.post(
            reverse('watchlist:edit-description', kwargs={'pk': self.watchlist.pk}),
            {'description': 'Hacked'}
        )
        self.assertEqual(response.status_code, 404)

    def test_redirects_if_not_logged_in(self):
        self.client.logout()
        response = self.client.get(
            reverse('watchlist:edit-description', kwargs={'pk': self.watchlist.pk})
        )
        self.assertNotEqual(response.status_code, 200)


class WatchlistDescriptionDeleteViewTest(WatchlistTestBase):

    def setUp(self):
        super().setUp()
        self.watchlist.description = 'Existing description'
        self.watchlist.save()

    def test_get_returns_200(self):
        response = self.client.get(
            reverse('watchlist:delete-description', kwargs={'pk': self.watchlist.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_clears_description_on_post(self):
        self.client.post(
            reverse('watchlist:delete-description', kwargs={'pk': self.watchlist.pk}),
            {'description': 'Existing description'}  # form needs current value
        )
        self.watchlist.refresh_from_db()
        self.assertEqual(self.watchlist.description, '')

    def test_other_user_cannot_delete_description(self):
        self.client.login(username='otheruser', password='pass')
        response = self.client.post(
            reverse('watchlist:delete-description', kwargs={'pk': self.watchlist.pk}),
            {'description': 'Existing description'}
        )
        self.assertEqual(response.status_code, 404)

    def test_redirects_on_success(self):
        response = self.client.post(
            reverse('watchlist:delete-description', kwargs={'pk': self.watchlist.pk}),
            {'description': 'Existing description'}
        )
        self.assertRedirects(response, reverse('watchlist:watchlist'))