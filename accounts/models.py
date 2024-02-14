# accounts/models.py

import uuid
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_save

# Create your models here.

class StallholderFilterManager(models.Manager):
    """
    Manager that returns all stallholders is accessed by calling
    CustomUser.stallholdermgr.all()
    """
    def get_queryset(self):
        return super().get_queryset().filter(role=3)


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
    reference_id = models.CharField(max_length=5, null=True)
    phone = models.CharField(max_length=13, unique=False)
    created_date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(default=timezone.now)

    objects = UserManager()
    stallholdermgr = StallholderFilterManager()


    def __str__(self):
        return self.first_name + ' ' + self.last_name

    def __unicode__(self):
        return '%s' % self.user


class Profile(models.Model):
    """
    Model linked to Customuser which is called and created when a new user is created
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    address1 = models.CharField(max_length=50, blank=True)
    address2 = models.CharField(max_length=50, blank=True)
    town = models.CharField(max_length=50, blank=True)
    postcode = models.CharField(max_length=10, blank=True)
    phone2 = models.CharField(max_length=13, blank=True)
    org_name = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.org_name

    """
    Hooking the create_user_profile and save_user_profile methods to the User model, whenever a save event occurs.
    This kind of signal is called post_save.
    """

    @receiver(post_save, sender=CustomUser)
    def create_user_profile(sender, instance, created, **kwargs):
        if kwargs.get('raw', False):
            return False
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=CustomUser)
    def save_user_profile(sender, instance, **kwargs):
        if kwargs.get('raw', False):
            return False
        instance.profile.save()



 
