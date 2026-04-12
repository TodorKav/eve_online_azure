import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eve.settings")
django.setup()

from eve.industry.db_fetching_scripts.tasks import fetch_all_types

fetch_all_types.delay()
print("✅ Task dispatched to Celery worker")