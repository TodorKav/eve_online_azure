from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from eve.accounts import views

app_name = 'accounts'
urlpatterns = [
    path('login/', LoginView.as_view(next_page='common:home'), name='login'),
    path('logout/', LogoutView.as_view(next_page='accounts:login'), name='logout'),
    path('register/', views.UserCreateView.as_view(), name='register'),
]