import random
import string
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
import datetime

from eve.accounts.models import CustomUser
from eve.eve_accounts.models import IngameAccounts


class EveAccountsTestBase(TestCase):

    def setUp(self):
        self.client = Client()

        self.user = CustomUser.objects.create_user(username="testuser", password="pass")
        self.other_user = CustomUser.objects.create_user(username="otheruser", password="pass")

        self.account = IngameAccounts.objects.create(
            user=self.user,
            character_id=12345,
            character_name="Test Character",
            refresh_token="a" * 40,
            access_token="b" * 40,
            expires_at=timezone.now() + datetime.timedelta(hours=2),
        )

        self.client.login(username="testuser", password="pass")


class EveAccountsListViewTest(EveAccountsTestBase):

    def test_redirects_if_not_logged_in(self):
        self.client.logout()
        response = self.client.get(reverse("eve_accounts:view_list"))
        self.assertNotEqual(response.status_code, 200)

    def test_returns_200_for_logged_in_user(self):
        response = self.client.get(reverse("eve_accounts:view_list"))
        self.assertEqual(response.status_code, 200)

    def test_only_returns_current_users_accounts(self):
        IngameAccounts.objects.create(
            user=self.other_user,
            character_id=99999,
            character_name="Other Character",
        )
        response = self.client.get(reverse("eve_accounts:view_list"))
        for account in response.context["object_list"]:
            self.assertEqual(account.user, self.user)

    def test_does_not_return_other_users_accounts(self):
        other_account = IngameAccounts.objects.create(
            user=self.other_user,
            character_id=99999,
            character_name="Other Character",
        )
        response = self.client.get(reverse("eve_accounts:view_list"))
        ids = [a.pk for a in response.context["object_list"]]
        self.assertNotIn(other_account.pk, ids)


class AddEveAccountViewTest(EveAccountsTestBase):

    def _post(self, data):
        return self.client.post(reverse("eve_accounts:add_account"), data)

    def test_redirects_if_not_logged_in(self):
        self.client.logout()
        response = self.client.get(reverse("eve_accounts:add_account"))
        self.assertNotEqual(response.status_code, 200)

    def test_get_returns_200(self):
        response = self.client.get(reverse("eve_accounts:add_account"))
        self.assertEqual(response.status_code, 200)

    def test_get_prefills_random_initial_values(self):
        response = self.client.get(reverse("eve_accounts:add_account"))
        form = response.context["form"]
        self.assertIn("character_id", form.initial)
        self.assertIn("refresh_token", form.initial)
        self.assertIn("access_token", form.initial)

    def test_get_prefills_token_of_correct_length(self):
        response = self.client.get(reverse("eve_accounts:add_account"))
        form = response.context["form"]
        self.assertEqual(len(form.initial["refresh_token"]), 40)
        self.assertEqual(len(form.initial["access_token"]), 40)

    def test_creates_account_assigned_to_current_user(self):
        initial_count = IngameAccounts.objects.filter(user=self.user).count()
        self._post({
            "character_id": 54321,
            "character_name": "New Character",
            "refresh_token": "r" * 40,
            "access_token": "a" * 40,
        })
        self.assertEqual(IngameAccounts.objects.filter(user=self.user).count(), initial_count + 1)

    def test_redirects_on_success(self):
        response = self._post({
            "character_id": 54321,
            "character_name": "New Character",
            "refresh_token": "r" * 40,
            "access_token": "a" * 40,
        })
        self.assertRedirects(response, reverse("eve_accounts:view_list"))

    def test_sets_expires_at_on_creation(self):
        self._post({
            "character_id": 54321,
            "character_name": "New Character",
            "refresh_token": "r" * 40,
            "access_token": "a" * 40,
        })
        account = IngameAccounts.objects.get(character_id=54321)
        self.assertIsNotNone(account.expires_at)

    def test_cannot_create_duplicate_character_id(self):
        initial_count = IngameAccounts.objects.count()
        self._post({
            "character_id": self.account.character_id,  # already exists
            "character_name": "Duplicate",
            "refresh_token": "r" * 40,
            "access_token": "a" * 40,
        })
        self.assertEqual(IngameAccounts.objects.count(), initial_count)

    def test_does_not_assign_other_user_on_creation(self):
        self._post({
            "character_id": 54321,
            "character_name": "New Character",
            "refresh_token": "r" * 40,
            "access_token": "a" * 40,
        })
        account = IngameAccounts.objects.get(character_id=54321)
        self.assertEqual(account.user, self.user)


class EveAccountsDeleteViewTest(EveAccountsTestBase):

    def test_redirects_if_not_logged_in(self):
        self.client.logout()
        response = self.client.get(
            reverse("eve_accounts:delete_account", kwargs={"pk": self.account.pk})
        )
        self.assertNotEqual(response.status_code, 200)

    def test_get_returns_200(self):
        response = self.client.get(
            reverse("eve_accounts:delete_account", kwargs={"pk": self.account.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_delete_form_in_context(self):
        response = self.client.get(
            reverse("eve_accounts:delete_account", kwargs={"pk": self.account.pk})
        )
        self.assertIn("form", response.context)

    def test_deletes_account_on_post(self):
        self.client.post(
            reverse("eve_accounts:delete_account", kwargs={"pk": self.account.pk})
        )
        self.assertFalse(IngameAccounts.objects.filter(pk=self.account.pk).exists())

    def test_redirects_after_delete(self):
        response = self.client.post(
            reverse("eve_accounts:delete_account", kwargs={"pk": self.account.pk})
        )
        self.assertRedirects(response, reverse("eve_accounts:view_list"))

    def test_other_user_cannot_delete_account(self):
        self.client.login(username="otheruser", password="pass")
        self.client.post(
            reverse("eve_accounts:delete_account", kwargs={"pk": self.account.pk})
        )
        self.assertTrue(IngameAccounts.objects.filter(pk=self.account.pk).exists())

    def test_other_user_gets_404_on_delete(self):
        self.client.login(username="otheruser", password="pass")
        response = self.client.post(
            reverse("eve_accounts:delete_account", kwargs={"pk": self.account.pk})
        )
        self.assertEqual(response.status_code, 404)


class EveAccountsEditViewTest(EveAccountsTestBase):

    def test_redirects_if_not_logged_in(self):
        self.client.logout()
        response = self.client.get(
            reverse("eve_accounts:edit_account", kwargs={"pk": self.account.pk})
        )
        self.assertNotEqual(response.status_code, 200)

    def test_get_returns_200(self):
        response = self.client.get(
            reverse("eve_accounts:edit_account", kwargs={"pk": self.account.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_updates_character_name(self):
        self.client.post(
            reverse("eve_accounts:edit_account", kwargs={"pk": self.account.pk}),
            {
                "character_id": self.account.character_id,
                "character_name": "Updated Name",
                "refresh_token": self.account.refresh_token,
                "access_token": self.account.access_token,
            },
        )
        self.account.refresh_from_db()
        self.assertEqual(self.account.character_name, "Updated Name")

    def test_redirects_on_success(self):
        response = self.client.post(
            reverse("eve_accounts:edit_account", kwargs={"pk": self.account.pk}),
            {
                "character_id": self.account.character_id,
                "character_name": "Updated Name",
                "refresh_token": self.account.refresh_token,
                "access_token": self.account.access_token,
            },
        )
        self.assertRedirects(response, reverse("eve_accounts:view_list"))

    def test_other_user_cannot_edit_account(self):
        self.client.login(username="otheruser", password="pass")
        self.client.post(
            reverse("eve_accounts:edit_account", kwargs={"pk": self.account.pk}),
            {
                "character_id": self.account.character_id,
                "character_name": "Hacked Name",
                "refresh_token": self.account.refresh_token,
                "access_token": self.account.access_token,
            },
        )
        self.account.refresh_from_db()
        self.assertNotEqual(self.account.character_name, "Hacked Name")

    def test_other_user_gets_404_on_edit(self):
        self.client.login(username="otheruser", password="pass")
        response = self.client.get(
            reverse("eve_accounts:edit_account", kwargs={"pk": self.account.pk})
        )
        self.assertEqual(response.status_code, 404)