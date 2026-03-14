from django.http import HttpResponseRedirect

from eve.watchlist.models import Watchlist


class WatchlistNameValidationMixin:
    def form_valid(self, form):
        self.object = form.save(commit=False)

        qs = Watchlist.objects.filter(user=self.object.user, name=self.object.name)
        if self.object.pk:
            qs = qs.exclude(pk=self.object.pk)

        if qs.exists():
            form.add_error('name', 'A watchlist with this name already exists.')
            return self.form_invalid(form)

        self.object.save()
        return HttpResponseRedirect(self.get_success_url())