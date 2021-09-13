# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


class CustomUser(AbstractUser):
    # Add additional fields

    def __str__(self):
        return self.email
