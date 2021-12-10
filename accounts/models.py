# accounts/models.py

import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from django.dispatch import receiver
from django.db.models.signals import post_save

# Create your models here.

phone_regex = RegexValidator(
    regex=r'/^(\((03|04|06|07|09)\)\d{7})|(\((021|022|025|027|028|029)\)\d{6,8})|((0508|0800|0900)\d{5,8})$/')


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
        return self.first_name + ' ' + self.last_name

    def __unicode__(self):
        return '%s' % self.user


class Profile(models.Model):
    """
    Model linked to Customuser which is called and created when a new user is created
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    address1 = models.CharField(max_length=50, blank=True, null=True)
    address2 = models.CharField(max_length=50, blank=True, null=True)
    town = models.CharField(max_length=50, blank=True, null=True)
    postcode = models.CharField(max_length=10, blank=True, null=True)
    phone2 = models.CharField(validators=[phone_regex], max_length=13, blank=True, null=True)
    org_name = models.CharField(max_length=50, blank=True, null=True)

    @receiver(post_save, sender=CustomUser)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(customuser=instance)

    @receiver(post_save, sender=CustomUser)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()



 
