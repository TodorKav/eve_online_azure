from django.urls import path, include


from eve.industry import views

app_name = 'industry'
urlpatterns = [
    path('', views.ItemList.as_view(), name='itemlist'),
    path('api/', include([
        path('categories/', views.CategoriesListApiView.as_view(), name='categories-list-api'),
        path('groups/', views.GroupsListApiView.as_view(), name='groups-list-api'),
        path('market_groups/', views.MarketGroupsListApiView.as_view(), name='market-groups-list-api'),
        path('types/', views.TypesListApiView.as_view(), name='types-list-api'),
        path('market_prices/', views.MarketPricesListApiView.as_view(), name='market-prices-list-api'),
        path('corporation_with_lp_stores/', views.CorporationsWithLPStoresListApiView.as_view(), name='corporation-with-lp-stores-list-api'),
        path('corporation_lp_item_types/', views.CorporationsLpItemTypesListApiView.as_view(), name='corporation-lp-item-types-list-api'),
        path('price_pro_lp/', views.ItemListApiView.as_view(), name='items-list-api'),
    ]))

]