from django.db.models import Q
from django.views.generic import ListView, TemplateView
from django.views.generic.edit import BaseFormView

from eve.industry.forms import SearchForm
from eve.industry.mixins import RequiredItemsMixin
from eve.industry.models import CorporationsLpItemTypes


# Create your views here.


class ItemList(ListView, BaseFormView):
    template_name = 'industry/items_list.html'
    model = CorporationsLpItemTypes
    form_class = SearchForm
    paginate_by = 50

    def get_queryset(self):
        if not hasattr(self, '_cached_queryset'):
            queryset = super().get_queryset()

            q = self.request.GET.get('q')
            if q:
                queryset = queryset.filter(Q(type_id__name__icontains=q) | Q(corporation_id__name=q))

            queryset = queryset.select_related('type_id', 'type_id__market_prices', 'corporation_id',)

            queryset = RequiredItemsMixin.display(queryset)

            self._cached_queryset = sorted(queryset, key=lambda x: x.price_pro_lp, reverse=True)
        return self._cached_queryset

    def get_initial(self):
        initial = super().get_initial()
        initial['q'] = self.request.GET.get('q')
        return initial
