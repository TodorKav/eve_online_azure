import os
import django
from tqdm import tqdm

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eve.settings")
django.setup()

import requests
from django.db import transaction
from eve.industry.models import Types, Groups, MarketGroups

url_categories = 'https://esi.evetech.net/universe/types/'

TIMEOUT = (15, 30)

session = requests.Session()
pages = int(session.get(url_categories, timeout=TIMEOUT).headers.get("X-Pages", 1))
type_list = []
for page in tqdm(range(1, pages + 1)):
    type_list += (session.get(f'{url_categories}?page={page}', timeout=TIMEOUT).json())

# due to inconsistency in the ESI (Eve API) there are Types-class objects with invalid groups__id's or market__id's.
# The goal here is to add None as a foreign key, if the provided groups_id or market_id is not a valid foreign key.
valid_group_ids = set(Groups.objects.values_list('group_id', flat=True))
valid_market_group_ids = set(MarketGroups.objects.values_list('market_group_id', flat=True))


with transaction.atomic():
    object_list = []
    for type_id in tqdm(type_list):
        obj_json = session.get(f'{url_categories}{type_id}/', timeout=TIMEOUT).json()

        gid = obj_json.get('group_id')
        mgid = obj_json.get('market_group_id')

        object_list.append(Types(
            type_id=obj_json.get('type_id'),
            group_id_id=gid if gid in valid_group_ids else None,
            market_group_id_id=mgid if mgid in valid_market_group_ids else None,
            name=obj_json.get('name'),
            description=obj_json.get('description'),
            capacity=obj_json.get('capacity'),
            mass=obj_json.get('mass'),
            volume=obj_json.get('volume'),
            packaged_volume=obj_json.get('packaged_volume'),
            radius=obj_json.get('radius'),
            portion_size=obj_json.get('portion_size'),
            graphic_id=obj_json.get('graphic_id'),
            icon_id=obj_json.get('icon_id'),
            published = obj_json.get('published'),
        ))
    Types.objects.bulk_create(object_list,
                                     update_conflicts=True,
                                     update_fields=['group_id', 'market_group_id', 'name',
                                                    'description', 'capacity', 'mass', 'volume',
                                                    'packaged_volume', 'radius', 'portion_size',
                                                    'graphic_id', 'icon_id', 'published', 'created_at'],
                                     unique_fields=['type_id',],
                                     batch_size=1000)
