from django.apps import AppConfig


class WatchlistConfig(AppConfig):
    name = 'eve.watchlist'

    def ready(self):
        import eve.watchlist.signals
