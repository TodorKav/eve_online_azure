from django.urls import path, include
from eve.eve_accounts import views

app_name = 'eve_accounts'

urlpatterns = [
    path('', views.EveAccountsListView.as_view(), name='view_list'),
    path('add_account/', views.AddEveAccountView.as_view(), name='add_account'),
    path('<int:pk>/', include([
        path('delete/', views.EveAccountsDeleteView.as_view(), name='delete_account'),
        path('edit/', views.EveAccountsEditView.as_view(), name='edit_account'),
    ])),
]