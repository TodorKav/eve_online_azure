from django import forms

from eve.eve_accounts.models import IngameAccounts

class IngameAccountsForm(forms.ModelForm):
    character_id = forms.IntegerField(widget=forms.NumberInput(attrs={'readonly': 'readonly'}))
    refresh_token = forms.CharField(widget=forms.Textarea(attrs={'rows': 2, 'readonly': 'readonly'}))
    access_token = forms.CharField(widget=forms.Textarea(attrs={'rows': 2, 'readonly': 'readonly'}))
    class Meta:
        model = IngameAccounts
        fields = ('character_id', 'character_name', 'refresh_token', 'access_token')

class AddIngameAccountForm(IngameAccountsForm):
    pass

class DeleteIngameAccountForm(IngameAccountsForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['disabled'] = True

class EditIngameAccountForm(IngameAccountsForm):
    pass