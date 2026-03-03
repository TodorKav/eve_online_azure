from django import forms


class SearchForm(forms.Form):
    q = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Type Item or Corporation', }))
