from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView
from django.urls import path, include, reverse_lazy
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from eve.accounts import views

app_name = 'accounts'
urlpatterns = [
    path('login/', LoginView.as_view(next_page='common:home'), name='login'),
    path('logout/', LogoutView.as_view(next_page='accounts:login'), name='logout'),
    path('register/', views.UserCreateView.as_view(), name='register'),
    path('password-change/', PasswordChangeView.as_view(success_url=reverse_lazy('accounts:password_change_done')), name='password_change'), # създай темплейта, свържи този и едита в профил детайли
    path('password-change-done/', PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('profile-detail/', views.ProfileDetailView.as_view(), name='profile_detail'),
    path('edit/', views.UserEditView.as_view(), name='edit_profile'),
    path('api/', include([
        path('create_user/', views.UserCreateApiView.as_view(), name='create_user'),
        path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    ]))
]