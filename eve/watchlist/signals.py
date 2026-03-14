from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from eve.watchlist.models import Watchlist
UserModel = get_user_model()

@receiver(post_save, sender=UserModel)
def create_watchlist(sender, instance, created, **kwargs):
    if created:
        Watchlist.objects.create(user=instance)