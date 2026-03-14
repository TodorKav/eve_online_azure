from django import forms

from eve.watchlist.models import Watchlist


class WatchlistForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Enter Watchlist name'}))

    class Meta:
        model = Watchlist
        fields = ('name',)


class WatchlistEditForm(WatchlistForm):
    pass

class WatchlistDeleteForm(WatchlistForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'disabled':'disabled'}))




