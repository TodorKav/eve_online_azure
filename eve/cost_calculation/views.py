from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Model, Prefetch
from django.shortcuts import render
from django.views.generic import DetailView

from eve.watchlist.models import Watchlist, WatchlistItem


# Create your views here.


class CostCalculation(LoginRequiredMixin, DetailView):
    template_name = 'cost_calculation/cost_calculation.html'
    model = Watchlist

    def get_queryset(self):
        queryset = (
            Watchlist.objects.prefetch_related(
                    Prefetch('items', queryset=WatchlistItem.objects.select_related('item', 'corporation')
                    .prefetch_related('corporation__lp_store_offers')))
                    .filter(user_id=self.request.user, id=self.kwargs.get('pk')))
        return queryset

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #
    #     item_dict = {}
    #     x = self.object.items.all().corporation
    #
    #     print(x)
    #
    #
    #
    #
    #
    #     return context