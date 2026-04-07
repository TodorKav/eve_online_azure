import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from eve.watchlist.forms import WatchlistForm, WatchlistEditForm, WatchlistDeleteForm
from eve.watchlist.mixins import WatchlistNameValidationMixin
from eve.watchlist.models import Watchlist, WatchlistItem


# Create your views here.

class WatchlistView(LoginRequiredMixin, ListView):
    template_name = 'watchlist/view_list.html'
    model = Watchlist

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user).prefetch_related('items__item', 'items__corporation')
        return queryset


@login_required
def add_items(request):
    object_list = []
    if request.method == 'POST':

        try:
            watchlist_id = Watchlist.objects.get(user=request.user, name__exact='Unsorted')
        except Watchlist.DoesNotExist:
            return render (request, 'watchlist/signal_error.html')


        selected_items = request.POST.getlist('selected_items')
        for selected_item in selected_items:
            selected_item = json.loads(selected_item)
            object_list.append(WatchlistItem(
                watchlist=watchlist_id,
                item_id=selected_item.get('type_id'),
                corporation_id=selected_item.get('corporation_id')))

        WatchlistItem.objects.bulk_create(object_list,
                                            update_conflicts=True,
                                            unique_fields=['item', 'corporation', 'watchlist',],
                                            update_fields=['created_at',])
    return redirect('watchlist:watchlist')


class AddTableView(WatchlistNameValidationMixin, CreateView):
    template_name = 'watchlist/add_table.html'
    success_url = reverse_lazy('watchlist:watchlist')
    model = Watchlist
    form_class =WatchlistForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        form.instance.user = self.request.user
        return super().form_valid(form)



class EditTableView(WatchlistNameValidationMixin, UpdateView):
    template_name = 'watchlist/edit_table.html'
    success_url = reverse_lazy('watchlist:watchlist')
    model = Watchlist
    form_class = WatchlistEditForm



class DeleteTableView(DeleteView):
    template_name = 'watchlist/delete_table.html'
    success_url = reverse_lazy('watchlist:watchlist')
    model = Watchlist

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = WatchlistDeleteForm(instance=self.object)
        return context

    def form_valid(self, form):
        success_url = self.get_success_url()
        if self.object.name == 'Unsorted':
            return HttpResponseRedirect(success_url)
        else:
            self.object.delete()
        return HttpResponseRedirect(success_url)

class MoveItemsView(View):

    def post(self, request, *args, **kwargs):

        items = request.POST.getlist('target_watchlist')
        item_list = [json.loads(item) for item in items]

        move_items_id = list(map(int, request.POST.getlist('move')))

        if not move_items_id:
            return redirect('watchlist:watchlist')

        for item in item_list:
            if item.get('watchlist_item_entry') in move_items_id:
                if item.get('current_watchlist') != item.get('target_watchlist'):
                    WatchlistItem.objects.filter(pk=item.get('watchlist_item_entry')).delete()
                    WatchlistItem.objects.get_or_create(
                        watchlist_id=item.get('target_watchlist'),
                        item_id=item.get('type_id'),
                        corporation_id=item.get('corporation_id'),
                    )

        return redirect('watchlist:watchlist')


