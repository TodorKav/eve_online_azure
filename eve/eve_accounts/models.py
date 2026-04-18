from django.contrib.auth import get_user_model
from django.db import models

# Create your models here.


Usermodel = get_user_model()

class IngameAccounts(models.Model):
    user = models.ForeignKey(to=Usermodel, on_delete=models.CASCADE)
    character_id = models.IntegerField(blank=True, null=True, unique=True)
    character_name = models.CharField(max_length=255)
    refresh_token = models.TextField(max_length=255, blank=True, null=True)
    access_token = models.TextField(max_length=255, blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)