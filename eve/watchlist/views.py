from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from eve.watchlist.models import Watchlist

# Create your views here.

class WatchlistView(LoginRequiredMixin, ListView):
    template_name = 'watchlist/view_list.html'
    model = Watchlist

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user).prefetch_related('items__item')
        return queryset
