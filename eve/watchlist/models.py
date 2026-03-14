from django.db import models

from eve.industry.mixins import CreatedAtMixin


# Create your models here.

class Watchlist(models.Model):
    user = models.ForeignKey(to='accounts.CustomUser', on_delete=models.CASCADE, related_name="watchlist")
    name = models.CharField(max_length=200, default="Unsorted")

    class Meta:
        unique_together = ("user", "name")


class WatchlistItem(CreatedAtMixin):
    watchlist = models.ForeignKey(to='Watchlist', on_delete=models.CASCADE, related_name="items")
    item = models.ForeignKey(to="industry.Types", on_delete=models.CASCADE, related_name="watchlist_entries")
    corporation = models.ForeignKey(to='industry.CorporationsWithLPStores', on_delete=models.CASCADE, related_name="watchlist_entries")

    class Meta:
        unique_together = ("watchlist", "item", "corporation")


