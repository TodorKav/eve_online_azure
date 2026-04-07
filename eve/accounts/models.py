from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class CustomUser(AbstractUser):
    first_name = None
    last_name = None

    def __str__(self):
        return self.username or 'No user'
