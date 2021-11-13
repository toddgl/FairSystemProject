# fairs/model.py

from django.db import models
from django.utils import timezone
from django.urls import reverse
from accounts.models import CustomUser
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.


class Fair(models.Model):
    """
    Description: Stores the details of each fair instance
    Uses a CharField for fair_year because we are going to convert
    that value to string for converting it to python datetime object.
    """

    fair_year = models.CharField(max_length=4, default='2022')
    fair_name = models.CharField(max_length=40)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    date_cancelled = models.DateTimeField(blank=True, default=None, null=True)
    fair_description = models.TextField()
    is_cancelled = models.BooleanField(default=False)
    activation_date = models.DateTimeField(blank=True, default=None, null=True)
    is_activated = models.BooleanField(default=False)
    created_by = models.ForeignKey(CustomUser, related_name='fair_created_by', on_delete=models.SET_NULL, blank=True,
                                   null=True)
    updated_by = models.ForeignKey(CustomUser, related_name='fair_updated_by', on_delete=models.SET_NULL, blank=True,
                                   null=True)

    def __str__(self):
        return self.fair_name

    class Meta:
        verbose_name_plural = "Fairs"

    def get_absolute_url(self):
        return reverse('fairs:fair-detail', args=[self.id])

    @property
    def get_fair_year(self):
        """
        Format it to datetime object. You need to convert `year`
        to str if it is `IntegerField`. ex: str(self.year).
        """
        date = timezone.datetime.strptime('%Y', self.fair_year)
        return date


class Zone(models.Model):
    """
    Description: Stores the details of the fair zones.
    """
    zone_name = models.CharField(max_length=40)
    zone_code = models.CharField(max_length=2, default=None, null=True)
    map_pdf = models.FileField(upload_to='media/maps')
    trestle_source = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(CustomUser, related_name='zone_created_by', on_delete=models.SET_NULL, blank=True,
                                   null=True)
    updated_by = models.ForeignKey(CustomUser, related_name='zone_updated_by', on_delete=models.SET_NULL, blank=True,
                                   null=True)

    def __str__(self):
        return self.zone_name

    class Meta:
        verbose_name_plural = "Zones"

    def get_absolute_url(self):
        return reverse('fairs:zone-detail', args=[self.id])


class InventoryItem(models.Model):
    """
    Description: A reference table for all that items that can be purchased by Stallholders
    when registering for a fair.  Uses two Joining tables: InvItemFair to capture items prices based on the fair, and
    InvItemEvent to capture the number of items consumed and available for each fair event
    """
    item_name = models.CharField(max_length=100)
    item_description = models.TextField()
    item_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(9999), ],)
    site_size = models.CharField(max_length=40)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(CustomUser, related_name='item_created_by', on_delete=models.SET_NULL, blank=True,
                                   null=True)
    updated_by = models.ForeignKey(CustomUser, related_name='item_updated_by', on_delete=models.SET_NULL, blank=True,
                                   null=True)

    def __str__(self):
        return self.item_name

    class Meta:
        verbose_name_plural = "InventoryItems"

    def get_absolute_url(self):
        return reverse('fairs:inventoryitem-detail', args=[self.id])


class Site(models.Model):
    """
    Description: Stores the details of the fair stallholder sites
    """
    site_name = models.CharField(max_length=40)
    site_size = models.ForeignKey(
        InventoryItem,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    zone = models.ForeignKey(
        Zone,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        CustomUser,
        related_name='site_created_by',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    updated_by = models.ForeignKey(
        CustomUser,
        related_name='site_updated_by',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    def __str__(self):
        return self.site_name

    class Meta:
        verbose_name_plural = "Sites"

    def get_absolute_url(self):
        return reverse('fairs:site-detail', args=[self.id])


class Event(models.Model):
    """
    Description: Stores the details of events associated with fair
    """
    event_name = models.CharField(max_length=40)
    original_event_date = models.DateField()
    postponement_event_date = models.DateField(blank=True, default=None, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    date_cancelled = models.DateTimeField(blank=True, default=None, null=True)
    event_description = models.TextField()
    is_cancelled = models.BooleanField(default=False)
    is_postponed = models.BooleanField(default=False)
    fair = models.ForeignKey(Fair, on_delete=models.CASCADE)
    sites = models.ManyToManyField(
        Site,
        related_name='events',
        through='EventSite',
    )
    created_by = models.ForeignKey(CustomUser, related_name='event_created_by', on_delete=models.SET_NULL, blank=True,
                                   null=True)
    updated_by = models.ForeignKey(CustomUser, related_name='event_updated_by', on_delete=models.SET_NULL, blank=True,
                                   null=True)

    def __str__(self):
        return self.event_name

    class Meta:
        verbose_name_plural = "Events"

    def get_absolute_url(self):
        return reverse('fairs:event-detail', args=[self.id])


class EventSite(models.Model):
    """
    Description: Junction table for the manytomany relationship between
    Events and Sites
    """

    AVAILABLE = 1
    ALLOCATED = 2
    PENDING = 3
    BOOKED = 4
    UNAVAILABLE = 5

    STATUS = (
        (AVAILABLE, _('Available to be booked')),
        (ALLOCATED, _('Allocated to a stallholder')),
        (PENDING, _('Pending finalisation of the booking')),
        (BOOKED, _('Booked')),
        (UNAVAILABLE, _('Not available for this event')),
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        verbose_name='event',
        related_name='event_sites'
    )
    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        verbose_name='site',
        related_name='event_sites'
    )
    status = models.PositiveSmallIntegerField(
        choices=STATUS,
        default=AVAILABLE,
    )

    class Meta:
        unique_together = ('event', 'site')
