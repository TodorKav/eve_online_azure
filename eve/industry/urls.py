from django.urls import path
from eve.industry import views

app_name = 'industry'
urlpatterns = [
    path('', views.ItemList.as_view(), name='itemlist'),
]