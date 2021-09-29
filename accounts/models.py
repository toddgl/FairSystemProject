# accounts/models.py

import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator

# Create your models here.


class CustomUser(AbstractUser):

    # these field tie to the roles
    ADMIN = 1
    CONVENER = 2
    STALLHOLDER = 3
    REGULATOR = 4

    ROLE_CHOICES = (
        (ADMIN, 'admin'),
        (CONVENER, 'convener'),
        (STALLHOLDER, 'stallholder'),
        (REGULATOR, 'regulator'),
    )

    phone_regex = RegexValidator(
        regex=r'/^(\((03|04|06|07|09)\)\d{7})|(\((021|022|025|027|028|029)\)\d{6,8})|((0508|0800|0900)\d{5,8})$/')

    class Meta:
        verbose_name = 'customuser'
        verbose_name_plural = 'customusers'

    # Add additional fields
    uid = models.UUIDField(unique=True, editable=False,
                           default=uuid.uuid4,
                           verbose_name='Public identifier')
    role = models.PositiveSmallIntegerField(
        choices=ROLE_CHOICES, blank=True, null=True, default=3)
    phone = models.CharField(
        validators=[phone_regex], max_length=13, unique=True, default='(027)1234567')
    created_date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
            return self.email
 
