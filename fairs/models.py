# fairs/model.py
from datetime import datetime
from django.db.models import Q, Case, F, When, DateField
from django.db import models
from django.urls import reverse
from accounts.models import CustomUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


# Global Variables
current_year = datetime.now().year
next_year = current_year + 1
four_years_past = current_year - 4


# Create your models here.


class Location(models.Model):
    """
    Description: A reference table FK relation for Zone so that Zones and Sites can be created for somewhere other than
    Martinborough
    """
    location_name = models.CharField(max_length=40, blank=True, null=True)

    def __str__(self):
        return self.location_name

    class Meta:
        verbose_name_plural = "Locations"


class InventoryItem(models.Model):
    """
    Description: A reference table for all that items that can be purchased by Stallholders
    when registering for a fair.  Uses two Joining tables: InvItemFair to capture items prices based on the fair, and
    InvItemEvent to capture the number of items consumed and available for each fair event
    """
    FAIRSITE = 1
    POWER = 2
    HEALTHSAFETY = 3
    FOODLICENCE = 4
    TRESTLE = 5
    VEHICLE = 6

    TYPE_CHOICE = [
        (FAIRSITE, _('Site')),
        (POWER, _('PowerPoint')),
        (HEALTHSAFETY, _('Health & Safety')),
        (FOODLICENCE, _('Food Licence')),
        (TRESTLE, _('Trestle')),
        (VEHICLE, _('Vehicle'))
    ]

    item_name = models.CharField(
        max_length=100,
        unique=True
    )
    item_type = models.PositiveSmallIntegerField(
        choices=TYPE_CHOICE,
        default=FAIRSITE
    )
    item_description = models.TextField()
    item_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(9999), ], )
    site_size = models.CharField(max_length=40, blank=True, null=True)
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


class CurrentFairManager(models.Manager):
    """
    Manager that returns the current Fair, accessed by calling
    Fair.currentfairmgr.all()
    """
    def get_queryset(self):
        return super().get_queryset().filter(fair_year__in=[current_year, next_year], is_activated=True).order_by('fair_year')


class Fair(models.Model):
    """
    Description: Stores the details of each fair instance
    Uses a CharField for fair_year because we are going to convert
    that value to string for converting it to python datetime object.
    """

    fair_year = models.CharField(max_length=4, default='2022')
    fair_name = models.CharField(
        max_length=40,
        unique=True
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    date_cancelled = models.DateTimeField(blank=True, default=None, null=True)
    fair_description = models.TextField()
    is_cancelled = models.BooleanField(default=False)
    activation_date = models.DateTimeField(blank=True, default=None, null=True)
    is_activated = models.BooleanField(default=False)
    allocation_email_date = models.DateTimeField(blank=True, default=None, null=True)
    created_by = models.ForeignKey(CustomUser, related_name='fair_created_by', on_delete=models.SET_NULL, blank=True,
                                   null=True)
    updated_by = models.ForeignKey(CustomUser, related_name='fair_updated_by', on_delete=models.SET_NULL, blank=True,
                                   null=True)
    inventory_items = models.ManyToManyField(
        InventoryItem,
        through='InventoryItemFair',
        related_name='fairs'
    )
    is_open = models.BooleanField(default=False)

    objects = models.Manager()
    currentfairmgr = CurrentFairManager()


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
        date = datetime.strptime(self.fair_year, '%Y')
        return date

    @property
    def has_reached_activation_date(self):
        if datetime.now() >= self.activation_date:
            return True
        return False


class Zone(models.Model):
    """
    Description: Stores the details of the fair zones.
    """
    RED = 1
    BLUE = 2

    TRESTLE_SOURCE_CHOICE = [
        (RED, _('Red')),
        (BLUE, _('Blue'))
    ]

    zone_name = models.CharField(
        max_length=40,
        unique=True
    )
    zone_code = models.CharField(max_length=2, default=None, null=True)
    trestle_source = models.PositiveSmallIntegerField(
        choices=TRESTLE_SOURCE_CHOICE,
        default=None,
        blank=True,
        null=True
    )
    location = models.ForeignKey(
        Location,
        related_name='zone_location',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
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


class CurrentInventoryItemFairManager(models.Manager):
    """
    Manager that returns the current InventoryItemFair, accessed by calling
    InventoryItemFair.currentinventoryitemfairmgr.all()
    """

    def get_queryset(self):
        return super().get_queryset().filter(fair__fair_year__in=[current_year, next_year], fair__is_activated=True)

    def full_size_site_price(self):
        return super().get_queryset().get(fair__fair_year__in=[current_year, next_year], fair__is_activated=True,
                                          inventory_item__item_name='Full Size Fair Site').price


    def half_size_site_price(self):
        return super().get_queryset().get(fair__fair_year__in=[current_year, next_year], fair__is_activated=True,
                                          inventory_item__item_name='Half Size Fair Site').price

    def trestle_table_price(self):
        return super().get_queryset().get(fair__fair_year__in=[current_year, next_year], fair__is_activated=True,
                                          inventory_item__item_name='Trestle Table').price

    def power_point_price(self):
        return super().get_queryset().get(fair__fair_year__in=[current_year, next_year], fair__is_activated=True,
                                          inventory_item__item_name='Power Point').price

    def health_safety_food_licence_price(self):
        return super().get_queryset().get(fair__fair_year__in=[current_year, next_year], fair__is_activated=True,
                                          inventory_item__item_name='Health & Safety Food Licence').price

    def food_licence_price(self):
        return super().get_queryset().get(fair__fair_year__in=[current_year, next_year], fair__is_activated=True,
                                          inventory_item__item_name='Foodstall Licence').price


class InventoryItemPriceManager(models.Manager):
    """
    Return the price of the inventory item when the fair id and inventory Item id are provided

    Usage:
        Returns the object - InventoryItemFair.inventoryitempricemgr.get_inventory_item_fair(5,4)
        Returns a field value in this case price -InventoryItemFair.inventoryitempricemgr.get_inventory_item_fair(5,4).price
    """
    def get_inventory_item_fair(self, fair_id, inventory_item_id):
        return super().get_queryset().get(fair=fair_id, inventory_item=inventory_item_id)


class InventoryItemFair(models.Model):
    """
    Description: Junction table for the manytomany relationship between
    InventoryItem and Fair
    """
    FAIRPRICE = 1
    DAILYPRICE = 2

    PRICING_CHOICE = [
        (FAIRPRICE, _('Fair Price')),
        (DAILYPRICE, _('Daily Price'))
    ]

    fair = models.ForeignKey(
        Fair,
        on_delete=models.CASCADE,
        verbose_name='fair',
        related_name='inventory_item_fair'
    )
    inventory_item = models.ForeignKey(
        InventoryItem,
        on_delete=models.CASCADE,
        verbose_name='inventory_items',
        related_name='inventory_itemr'
    )
    price_rate = models.PositiveSmallIntegerField(
        choices=PRICING_CHOICE,
        default=FAIRPRICE,
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_percentage = models.BooleanField(default=False)
    is_refundable = models.BooleanField(default=True)

    objects = models.Manager()
    currentinventoryitemfairmgr = CurrentInventoryItemFairManager()
    inventoryitempricemgr = InventoryItemPriceManager()

    def __int__(self):
        return str(self.inventory_item) + "$" + str(self.price)


class ZoneMap(models.Model):
    """
    Description: A linked model to Zone that supports the saving on Zone Site maps, the map saving functionality was
    moved from the Zone model so a history of past maps could be recorded against each Zone.
    """
    zone = models.ForeignKey(
        Zone,
        on_delete=models.CASCADE,
        verbose_name='zone',
        related_name='zone_map',
    )
    year = models.CharField(max_length=4, default=str(current_year))
    map_pdf = models.FileField(upload_to='maps/' + str(current_year))

    class Meta:
        unique_together = ('year', 'map_pdf')


class PowerBox(models.Model):
    """
    Description: Store the details of the power boxes used to provide power to stallholders
    """
    power_box_name = models.CharField(
        max_length=100,
        unique=True
    )
    power_box_description = models.TextField()
    socket_count = models.IntegerField()
    max_load = models.DecimalField(max_digits=10, decimal_places=4)
    zone = models.ForeignKey(
        Zone,
        on_delete=models.CASCADE,
        verbose_name='zone',
        related_name='powerbox'
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(CustomUser, related_name='powerbox_created_by',
                                   on_delete=models.SET_NULL, blank=True, null=True)
    updated_by = models.ForeignKey(CustomUser, related_name='powerbox_updated_by',
                                   on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.power_box_name


class Site(models.Model):
    """
    Description: Stores the details of the fair stallholder sites
    """
    site_name = models.CharField(
        max_length=40,
        unique= True
    )
    site_size = models.ForeignKey(
        InventoryItem,
        related_name='site_sizes',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    zone = models.ForeignKey(
        Zone,
        related_name='zones',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    is_active = models.BooleanField(default=True)
    has_power = models.BooleanField(default=False)
    powerbox = models.ForeignKey(
        PowerBox,
        on_delete=models.SET_NULL,
        verbose_name='powerbox',
        related_name='site_powerbox',
        blank = True,
        null = True
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
    site_note = models.TextField(null=True, blank=True, default=None)

    def __str__(self):
        return self.site_name

    class Meta:
        verbose_name_plural = "Sites"

    def get_absolute_url(self):
        return reverse('fairs:site-detail', args=[self.id])


class CurrentEventFilterManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(fair__fair_year__in=[current_year, next_year],
                                             fair__is_activated=True)

    def annotate_event_sequence(self):
        """
        Annotates the queryset with dynamically calculated event sequence
        based on the earliest date (original or postponement).
        """
        return self.get_queryset().annotate(
            actual_event_date=Case(
                When(postponement_event_date__isnull=False, then=F('postponement_event_date')),
                default=F('original_event_date'),
                output_field=DateField(),  # Explicitly specify the output field type
            )
        ).order_by('actual_event_date')

    def get_event_by_position(self, position):
        """
        Returns the event at the specified position based on chronological order.
        Position is 1-based (1 for first, 2 for second, etc.).
        """
        if position < 1:
            raise ValueError("Position must be a positive integer.")

        # Annotate and order events
        events = self.annotate_event_sequence()

        # Retrieve the event at the specified position
        try:
            return events[position - 1]  # Convert 1-based to 0-based index
        except IndexError:
            return None  # Return None if the position exceeds the queryset size


class Event(models.Model):
    """
    Description: Stores the details of events associated with fair
    """
    FIRSTEVENT = 1
    SECONDEVENT = 2

    EVENT_SEQUENCE_CHOICE = [
        (FIRSTEVENT, _('First Event')),
        (SECONDEVENT, _('Second Event'))
    ]

    event_name = models.CharField(
        max_length=40,
        unique=True
    )
    event_sequence = models.PositiveSmallIntegerField(
        choices=EVENT_SEQUENCE_CHOICE,
        default=FIRSTEVENT,
    )
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

    objects = models.Manager()
    currenteventfiltermgr = CurrentEventFilterManager()

    def __str__(self):
        return self.event_name

    class Meta:
        verbose_name_plural = "Events"

    def get_absolute_url(self):
        return reverse('fairs:event-detail', args=[self.id])


class EventSiteCurrentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(event__fair__fair_year__in=[current_year, next_year],
                                             event__fair__is_activated=True)


class SiteAvailableManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(site_status=1, event__fair__fair_year__in=[current_year, next_year],
                                             event__fair__is_activated=True)


class SiteAvailableFirstEventManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(site_status=1, event__event_sequence=1,
                                             event__fair__fair_year__in=[current_year, next_year],
                                             event__fair__is_activated=True)


class SiteAvailableSecondEventManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(site_status=1, event__event_sequence=2,
                                             event__fair__fair_year__in=[current_year, next_year],
                                             event__fair__is_activated=True)


class SiteAllocatedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(site_status=2)


class SitePendingManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(site_status=3)


class SiteBookedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(site_status=4)


class SiteUnavailableManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(site_status=5)


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
    ARCHIVED = 6

    SITE_STATUS_CHOICE = (
        (AVAILABLE, _('Available to be booked')),
        (ALLOCATED, _('Allocated to a stallholder')),
        (PENDING, _('Pending finalisation of the booking')),
        (BOOKED, _('Booked')),
        (UNAVAILABLE, _('Not available for this event')),
        (ARCHIVED, _('No longer used - was from a previous fair'))
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
    site_status = models.PositiveSmallIntegerField(
        choices=SITE_STATUS_CHOICE,
        default=AVAILABLE,
    )
    notes = models.TextField(null=True)

    objects = models.Manager()  # The default manager.
    eventsitecurrentmgr = EventSiteCurrentManager() # All sites for the current fair
    site_available = SiteAvailableManager()  # The site status available manager.
    site_allocated = SiteAllocatedManager()  # The site status allocated manager.
    site_pending = SitePendingManager()  # The site status pending manager.
    site_booked = SiteBookedManager()  # The site status booked manager.
    site_unavailable = SiteUnavailableManager()  # The site status unavailable manager.
    site_available_first_event = SiteAvailableFirstEventManager()  # The site status of available for first event
    site_available_second_event = SiteAvailableSecondEventManager()  # The site status of available for second event

    class Meta:
        unique_together = ('event', 'site')

    def __str__(self):
        return str(self.event) + " - " + str(self.site)


class EventPowerCurrentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(event__fair__fair_year__in=[current_year, next_year],
                                             event__fair__is_activated=True)


class EventPower(models.Model):
    """
    Description: Junction table for the manytomany relationship between
    Events and PowerBox
    """
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        verbose_name='event',
        related_name='event_power'
    )
    power_box = models.ForeignKey(
        PowerBox,
        on_delete=models.CASCADE,
        verbose_name='power_box',
        related_name='event_power'
    )
    sockets_used = models.IntegerField(
        default=0
    )
    power_load = models.DecimalField(max_digits=10, decimal_places=5)

    objects = models.Manager()  # The default manager.
    event_power_current_mgr = EventPowerCurrentManager()  # The event power status available manager.

    class Meta:
        unique_together = ('event', 'power_box')

class FourYearHistoryManager(models.Manager):
    """
    Manager that returns all the site history for the past four years of stallholder who are currently active
    SiteHistory.fouryearhistorymgr.all()
    """
    def get_queryset(self):
        return super().get_queryset().filter(year__lte=current_year,
                                             year__gte=four_years_past).order_by('year')

class CurrentFairSiteHistoryManager(models.Manager):
    """
    Manager that returns the site histy for the current Fair - SiteHistory.currentsitehistorymgr.all()
    """
    def get_queryset(self):
        current_fair_year = Fair.currentfairmgr.first().fair_year
        return super().get_queryset().filter(year=current_fair_year).order_by('site')


class SiteHistory(models.Model):
    """
    Description: A model to hold a summary of Stallholder Site History, initially used to store legacy data,
    but the main purpose is to automatically allocate sites based on site usage history.
    """
    stallholder = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='custom_user',
        related_name='site_history'
    )
    year = models.CharField(max_length=4, default='2022')
    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        verbose_name='site',
        related_name='site_history'
    )
    site_size = models.ForeignKey(
        InventoryItem,
        related_name='site_size_name',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    is_half_size = models.BooleanField(default=False)
    is_skipped = models.BooleanField(default=False)
    had_late_cancel = models.BooleanField(default=False)
    had_fair_site_move = models.BooleanField(default=False)
    number_events = models.IntegerField(default=0)
    history_note = models.TextField(null=True, blank=True, default=None)
    objects = models.Manager()
    fouryearhistorymgr = FourYearHistoryManager()
    currentsitehistorymgr = CurrentFairSiteHistoryManager()

    class Meta:
        unique_together = ('stallholder', 'site', 'year')


class CurrentSiteAllocationManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(event_site__event__fair__fair_year__in=[current_year, next_year],
                                             event_site__event__fair__is_activated=True)


class SiteAllocation(models.Model):
    """
    Description: A model to hold teh allocation of sites firstly based on historical Stallholder site preferences plus
    for the convener to handle request for site moves and allocation of sites to new stallholders
    """
    stallholder = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='stallholder',
        related_name='site_allocation'
    )
    event_site = models.ForeignKey(
        EventSite,
        on_delete=models.CASCADE,
        verbose_name='event_site',
        related_name='site_allocation'
    )
    stall_registration = models.ForeignKey(
        'registration.StallRegistration',
        verbose_name='stall_registration',
        related_name='site_allocation',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    event_power = models.ForeignKey(
        EventPower,
        verbose_name='event_power',
        related_name='site_allocation',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    created_by = models.ForeignKey(CustomUser, related_name='allocation_created_by', on_delete=models.SET_NULL,
                                   blank=True,
                                   null=True)
    updated_by = models.ForeignKey(CustomUser, related_name='allocation_updated_by', on_delete=models.SET_NULL,
                                   blank=True,
                                   null=True)
    on_hold = models.BooleanField(default=False) # Used to lock SiteAllocation when deleting unregistered allocations

    objects = models.Manager()  # The default manager.
    currentallocationsmgr = CurrentSiteAllocationManager()  # The current site siteallocations manager


    class Meta:
        unique_together = ('stallholder', 'event_site')
