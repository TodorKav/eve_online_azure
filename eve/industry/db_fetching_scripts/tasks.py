import requests
from celery import shared_task, group, chord
from django.db import transaction
from eve.industry.models import Types, Groups, MarketGroups
import time
import threading

URL_TYPES = 'https://esi.evetech.net/universe/types/'
TIMEOUT = (15, 30)
CHUNK_SIZE = 200  # types per worker task


# Shared error budget tracker across threads
error_budget_lock = threading.Lock()
error_budget = {"remaining": 100}

def fetch_type(session, type_id):
    for attempt in range(5):
        try:
            resp = session.get(f'{URL_TYPES}{type_id}/', timeout=TIMEOUT)

            # Track ESI error budget
            remaining = int(resp.headers.get('X-ESI-Error-Limit-Remain', 100))
            with error_budget_lock:
                error_budget["remaining"] = remaining

            # Back off aggressively if budget is low
            if remaining < 20:
                time.sleep(2)

            if resp.status_code == 420:
                retry_after = int(resp.headers.get('Retry-After', 60))
                print(f"Error budget exceeded, sleeping {retry_after}s")
                time.sleep(retry_after)
                continue

            if resp.status_code == 429:
                retry_after = int(resp.headers.get('Retry-After', 10))
                time.sleep(retry_after)
                continue

            resp.raise_for_status()
            return resp.json()

        except requests.RequestException as e:
            time.sleep(2 ** attempt)  # exponential backoff

    return None


@shared_task(bind=True, max_retries=3)
def fetch_and_save_type_chunk(self, type_ids: list):
    """
    Fetches a chunk of type IDs and bulk-upserts them.
    Runs in parallel across multiple Celery workers.
    """
    valid_group_ids = set(Groups.objects.values_list('group_id', flat=True))
    valid_market_group_ids = set(
        MarketGroups.objects.values_list('market_group_id', flat=True)
    )

    session = requests.Session()
    object_list = []

    for type_id in type_ids:
        obj_json = fetch_type(session, type_id)
        if obj_json is None:
            continue

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
            published=obj_json.get('published'),
        ))

    if object_list:
        with transaction.atomic():
            Types.objects.bulk_create(
                object_list,
                update_conflicts=True,
                update_fields=[
                    'group_id', 'market_group_id', 'name', 'description',
                    'capacity', 'mass', 'volume', 'packaged_volume', 'radius',
                    'portion_size', 'graphic_id', 'icon_id', 'published', 'created_at'
                ],
                unique_fields=['type_id'],
            )

    return len(object_list)


@shared_task
def log_completion(results):
    """Called after all chunks finish (chord callback)."""
    total = sum(r for r in results if r)
    print(f"✅ Sync complete. Total types upserted: {total}")


@shared_task(bind=True)
def fetch_all_types(self):
    """
    Coordinator task:
    1. Fetches all type IDs (paginated)
    2. Splits into chunks
    3. Dispatches parallel worker tasks via chord
    """
    session = requests.Session()

    # Step 1: collect all type_ids across pages
    resp = session.get(URL_TYPES, timeout=TIMEOUT)
    pages = int(resp.headers.get("X-Pages", 1))

    type_list = []
    for page in range(1, pages + 1):
        page_resp = session.get(f'{URL_TYPES}?page={page}', timeout=TIMEOUT)
        type_list.extend(page_resp.json())

    print(f"📦 Found {len(type_list)} types across {pages} pages")

    # Step 2: split into chunks
    chunks = [
        type_list[i:i + CHUNK_SIZE]
        for i in range(0, len(type_list), CHUNK_SIZE)
    ]

    # Step 3: dispatch parallel tasks, collect results via chord
    chord(
        group([fetch_and_save_type_chunk.s(chunk) for chunk in chunks])
    )(log_completion.s())