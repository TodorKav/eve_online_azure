from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView

from eve.accounts.forms import CustomUserCreationForm

# Create your views here.
UserModel = get_user_model()

class UserCreateView(UserPassesTestMixin, CreateView):
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')
    model = UserModel
    form_class = CustomUserCreationForm

    def test_func(self):
        if self.request.user.is_authenticated:
            return False
        return True
