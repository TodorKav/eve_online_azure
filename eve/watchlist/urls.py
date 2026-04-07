from django.urls import path, include, reverse_lazy
from django.views.generic import DeleteView

from eve.watchlist import views

app_name = 'watchlist'
urlpatterns = [
    path('', views.WatchlistView.as_view(), name='watchlist'),
    path('watchlist_items_save/', views.add_items, name='watchlist-items-save'),
    path('add_table/', views.AddTableView.as_view(), name='add-table'),
    path('move_items/', views.MoveItemsView.as_view(), name='move-items'),
    path('<int:pk>/', include([
        path('edit_table/', views.EditTableView.as_view(), name='edit-table'),
        path('delete_table/', views.DeleteTableView.as_view(), name='delete-table'),
        path('watchlist_edit_description/', views.WatchlistDescriptionEditView.as_view(), name='edit-description'),
        path('watchlist_delete_description/', views.WatchlistDescriptionDeliteView.as_view(), name='delete-description'),
    ])),
    path('delete_items/<int:pk>/', DeleteView.as_view(
        model=views.WatchlistItem,
        success_url=reverse_lazy('watchlist:watchlist')
    ), name='delete-items'),
]