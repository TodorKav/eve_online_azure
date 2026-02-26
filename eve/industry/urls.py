from django.urls import path
from eve.industry import views
urlpatterns = [
    path('', views.ItemList.as_view(), name='test'),
]