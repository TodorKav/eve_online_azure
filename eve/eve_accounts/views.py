import datetime
import random
import string

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, CreateView, DetailView, DeleteView, UpdateView

from eve.eve_accounts.forms import AddIngameAccountForm, DeleteIngameAccountForm, EditIngameAccountForm
from eve.eve_accounts.models import IngameAccounts


# Create your views here.

class EveAccountsListView(LoginRequiredMixin, ListView):
    template_name = 'eve_accounts/view_list.html'
    model = IngameAccounts

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset

class AddEveAccountView(LoginRequiredMixin, CreateView):
    RANDOM_STRING = string.ascii_letters + string.digits

    template_name = 'eve_accounts/add_account.html'
    success_url = reverse_lazy('eve_accounts:view_list')
    model = IngameAccounts
    form_class = AddIngameAccountForm

    def get_initial(self):
        kwargs = super().get_initial()
        random_number = random.randint(1, 1000)
        kwargs['character_id'] = random_number
        kwargs['refresh_token'] = ''.join(random.choice(self.RANDOM_STRING) for _ in range(40))
        kwargs['access_token'] = ''.join(random.choice(self.RANDOM_STRING) for _ in range(40))
        return kwargs

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.user = self.request.user
        instance.expires_at = timezone.now() + datetime.timedelta(hours=2)
        instance.save()
        self.object = instance
        return HttpResponseRedirect(self.get_success_url())


class EveAccountsDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'eve_accounts/delete_account.html'
    success_url = reverse_lazy('eve_accounts:view_list')
    model = IngameAccounts

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = DeleteIngameAccountForm(instance=self.object)
        return context

class EveAccountsEditView(LoginRequiredMixin, UpdateView):
    template_name = 'eve_accounts/edit_account.html'
    success_url = reverse_lazy('eve_accounts:view_list')
    model = IngameAccounts
    form_class = EditIngameAccountForm

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset