import os

import django
from tqdm import tqdm

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eve.settings")
django.setup()

import requests
from django.db import transaction
from eve.industry.models import CorporationsLpItemTypes, CorporationsWithLPStores

url_categories = 'https://esi.evetech.net/loyalty/stores/'

TIMEOUT = (15, 30)

session = requests.Session()
corporation_id_list = CorporationsWithLPStores.objects.values_list('corporation_id', flat=True)


# to = []


with transaction.atomic():
    lp_store_items = {}
    for corporation in tqdm(corporation_id_list):
        offered_items = session.get(f'{url_categories}{corporation}/offers/', timeout=TIMEOUT).json()
        for item in offered_items:
            key = (item.get('type_id'), corporation)


            # if key in lp_store_items:
            #     to.append(key)
# проблемен type_id, corporation -> [(87982, 1000004), (87982, 1000004)]


            lp_store_items[key] = (CorporationsLpItemTypes(
                type_id_id=item.get('type_id'),
                corporation_id_id=corporation,
                ak_cost=item.get('ak_cost'),
                isk_cost=item.get('isk_cost'),
                lp_cost=item.get('lp_cost'),
                offer_id=item.get('offer_id'),
                quantity=item.get('quantity'),
                required_items=item.get('required_items'),
            ))
    CorporationsLpItemTypes.objects.bulk_create(lp_store_items.values(),
                               update_conflicts=True,
                               update_fields=['ak_cost', 'isk_cost', 'lp_cost', 'offer_id', 'quantity', 'required_items'],
                               unique_fields=['type_id', 'corporation_id'],
                               batch_size=1000)






# print(to)
# Това е проблемният артикул, има резлика в количеството
    # {
    #     "ak_cost": 0,
    #     "isk_cost": 0,
    #     "lp_cost": 0,
    #     "offer_id": 19441,
    #     "quantity": 10,
    #     "required_items": [
    #         {
    #             "quantity": 10,
    #             "type_id": 87618
    #         }
    #     ],
    #     "type_id": 87982
    # },
    #
    #
    # {
    #     "ak_cost": 0,
    #     "isk_cost": 0,
    #     "lp_cost": 0,
    #     "offer_id": 19442,
    #     "quantity": 50,
    #     "required_items": [
    #         {
    #             "quantity": 50,
    #             "type_id": 87618
    #         }
    #     ],
    #     "type_id": 87982
    # },
    #
    #
    # {
    #     "ak_cost": 0,
    #     "isk_cost": 0,
    #     "lp_cost": 0,
    #     "offer_id": 19440,
    #     "quantity": 1,
    #     "required_items": [
    #         {
    #             "quantity": 1,
    #             "type_id": 87618
    #         }
    #     ],
    #     "type_id": 87982
    # },

















































# import os
#
# import django
# from tqdm import tqdm
#
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eve.settings")
# django.setup()
#
# import requests
# from django.db import transaction
# from eve.industry.models import CorporationsLpItemTypes, CorporationsWithLPStores
#
# url_categories = 'https://esi.evetech.net/loyalty/stores/'
#
# TIMEOUT = (15, 30)
#
# session = requests.Session()
# corporation_id_list = CorporationsWithLPStores.objects.values_list('corporation_id', flat=True)
# corporation_id_list = corporation_id_list[:10]
#
# with transaction.atomic():
#     lp_store_items = []
#     for corporation in tqdm(corporation_id_list):
#         offered_items = session.get(f'{url_categories}{corporation}/offers/', timeout=TIMEOUT).json()
#         for item in offered_items:
#             lp_store_items.append(CorporationsLpItemTypes(
#                 type_id_id=item.get('type_id'),
#                 corporation_id_id=corporation,
#                 ak_cost=item.get('ak_cost'),
#                 isk_cost=item.get('isk_cost'),
#                 lp_cost=item.get('lp_cost'),
#                 offer_id=item.get('offer_id'),
#                 quantity=item.get('quantity'),
#                 required_items=item.get('required_items'),
#             ))
#     CorporationsLpItemTypes.objects.bulk_create(lp_store_items,
#                                update_conflicts=True,
#                                update_fields=['ak_cost', 'isk_cost', 'lp_cost', 'offer_id', 'quantity', 'required_items'],
#                                unique_fields=['type_id', 'corporation_id'],
#                                batch_size=1000)
