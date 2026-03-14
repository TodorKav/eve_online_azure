from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, TemplateView

from eve.accounts.forms import CustomUserCreationForm, CustomUserChangeForm

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


class UserEditView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    template_name = 'accounts/profile_edit.html'
    model = UserModel
    form_class = CustomUserChangeForm
    success_message = "Your profile was successfully updated."

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('accounts:profile_detail')


class ProfileDetailView(LoginRequiredMixin, TemplateView,):
    template_name = 'accounts/profile_detail.html'

