from django.urls import path

from eve.watchlist import views

app_name = 'watchlist'
urlpatterns = [
    path('', views.WatchlistView.as_view(), name='watchlist'),
]