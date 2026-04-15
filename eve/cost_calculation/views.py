from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic import ListView

from eve.industry.models import CorporationsLpItemTypes, Types
from eve.watchlist.models import Watchlist


# Create your views here.


class CostCalculation(LoginRequiredMixin, ListView):
    template_name = 'cost_calculation/cost_calculation.html'
    model = Watchlist

    def get_queryset(self):
        get_result = self.request.GET
        result_list = []

        for key, value in get_result.items():
            if key.startswith('qty_'):
                type_id, corp_id = key[4:].split('_')
                result_list.append((int(type_id), int(corp_id), int(value)))

        result_dict = {}

        for type_id, corporation_id, qty in result_list:
            objs = CorporationsLpItemTypes.objects.filter(corporation_id=corporation_id, type_id=type_id)
            if objs.exists():
                obj = objs.first()
                if obj.id not in result_dict:
                    result_dict[obj.id] = (obj, qty)
                else:
                    result_dict[obj.id] = (obj, result_dict[obj.id][1] + qty)
            else:
                print(f"No CorporationsLpItemTypes found for corporation_id={corporation_id}, type_id={type_id}")

        required_items_dict = {}
        for result in result_dict:
            required_items = result_dict[result][0].required_items
            if required_items:
                for item in required_items:
                    if item.get('type_id') not in required_items_dict:
                        required_items_dict[item.get('type_id')] = item.get('quantity') * result_dict[result][1]
                    else:
                        required_items_dict[item.get('type_id')] += item.get('quantity') * result_dict[result][1]


        queryset = Types.objects.filter(type_id__in=required_items_dict.keys()).select_related('market_prices')

        total_price = 0
        for obj in queryset:
            obj.required_qty = required_items_dict.get(obj.type_id, 0)
            obj.total_multiplied = obj.required_qty * obj.market_prices.adjusted_price
            total_price += obj.total_multiplied
        queryset.total_price = total_price
        return queryset