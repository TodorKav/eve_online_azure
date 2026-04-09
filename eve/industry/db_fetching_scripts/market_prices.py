import os
import django
from tqdm import tqdm

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eve.settings")
django.setup()

import requests
from django.db import transaction
from eve.industry.models import MarketPrices, CorporationsLpItemTypes, Types

url_categories = 'https://esi.evetech.net/markets/prices'

TIMEOUT = (15, 30)

market_prices_list = requests.get(url_categories, timeout=TIMEOUT).json()

with transaction.atomic():
    object_list = []
    for item in tqdm(market_prices_list):
        object_list.append(MarketPrices(
            type_id_id=item.get('type_id'),
            adjusted_price=item.get('adjusted_price'),
            average_price=item.get('average_price'),
        ))
    MarketPrices.objects.bulk_create(object_list,
                                     update_conflicts=True,
                                     update_fields=['adjusted_price', 'average_price', 'created_at',],
                                     unique_fields=['type_id',],
                                     batch_size=1000)



##############################- Updating required and material_cost in CorporationsLpItemTypes-#########################
print("Calculating material costs...")
all_lp_items = (CorporationsLpItemTypes.objects.exclude(required_items=[]).exclude(required_items__isnull=True))
all_type_ids = set() # set af all type_id's in the required_items: {type_id, ...}
for obj in all_lp_items:
    for content in obj.required_items:
        all_type_ids.add(content.get('type_id'))

# Fetch all needed Types + their market prices in one query: {type_id: {'price': price, 'name': name}, }
type_data = {
    t.type_id: {
        'price': t.market_prices.adjusted_price if (hasattr(t, 'market_prices') and t.market_prices) else None,
        'name': t.name
    }
    for t in Types.objects.filter(type_id__in=all_type_ids).select_related('market_prices')
}

# Compute _cost_cost per LP item and bulk update
to_update = []
for obj in tqdm(all_lp_items, desc="Computing material costs"):
    material_cost = 0.0
    has_missing_price = False
    content_list = []  # column analog to required_items but with type_id.name and quantity, for template representation

    for content in obj.required_items:
        type_id = content.get('type_id')
        quantity = content.get('quantity', 0)
        data = type_data.get(type_id, {})
        price = data.get('price')
        name = data.get('name', str(type_id))

        if price is None:
            has_missing_price = True
        else:
            material_cost += price * quantity

        content_list.append(f'Item: {name} quantity: {quantity}.')

    obj.required = ', '.join(content_list)
    obj.material_cost = None if has_missing_price else material_cost
    to_update.append(obj)

CorporationsLpItemTypes.objects.bulk_update(
    to_update,
    fields=['material_cost', 'required'],
    batch_size=1000
)
print("Calculation finished")