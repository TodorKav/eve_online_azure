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


class WatchlistDescriptionForm(forms.ModelForm):
    class Meta:
        model = Watchlist
        fields = ('description',)

class WatchlistDescriptionEditForm(WatchlistDescriptionForm):
    description = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder':'Enter a Watchlist description if needed.', 'required': False}))


class WatchlistDescriptionDeleteForm(WatchlistDescriptionForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for value in self.fields.values():
            value.disabled = True
