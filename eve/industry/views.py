from django.views.generic import ListView

from eve.industry.mixins import RequiredItemsMixin
from eve.industry.models import CorporationsLpItemTypes


# Create your views here.


class ItemList(ListView):
    template_name = 'industry/items_list.html'
    model = CorporationsLpItemTypes
    paginate_by = 100000

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('type_id', 'type_id__market_prices', 'corporation_id',)
        queryset = RequiredItemsMixin.display(queryset)
        return queryset

