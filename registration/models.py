# registration/model.py

from django.conf import settings  # new
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_fsm import FSMField

from fairs.models import (
    Fair,
    InventoryItem
)

PERCENTAGE_VALIDATOR = [MinValueValidator(0), MaxValueValidator(100)]


class FoodPrepEquipment(models.Model):
    """
    Description: A reference table for storing electrical food preparation equipment and the electrical load that
    each will place on the fair electrical network
    """
    equipment_name = models.CharField(max_length=40)
    power_load_maximum = models.DecimalField(max_digits=10, decimal_places=2)
    power_load_minimum = models.DecimalField(max_digits=10, decimal_places=2)
    power_load_factor = models.DecimalField(max_digits=3, decimal_places=0, default=70, validators=PERCENTAGE_VALIDATOR)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='food_prep_equipment_created_by',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='food_prep_equipment_updated_by',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    def __str__(self):
        return self.equipment_name

    class Meta:
        verbose_name_plural = "FoodPrepEquipments"


class FoodSaleType(models.Model):
    """
    Description; Model that holds the definition of the various food sale types
    """
    food_sale_type = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='food_stall_type_created_by',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='food_stall_type_updated_by',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    def __str__(self):
        return self.food_sale_type

    class Meta:
        verbose_name_plural = "FoodStallTypes"


class StallCategory(models.Model):
    """
    Description: Model that holds the definition of Stall Categories
    """
    category_name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    has_inventory_item = models.BooleanField(default=False)
    inventory_item = models.ForeignKey(
        InventoryItem,
        related_name='inventory_item',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='stall_category_created_by',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='stall_category_updated_by',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    def __str__(self):
        return self.category_name

    class Meta:
        verbose_name_plural = "StallCategories"


class StallRegistration(models.Model):
    """
    Description: Model to capture stall registrations
    """
    CREATED = 'Created'
    SUBMITTED = 'Submitted'
    INVOICED = 'Invoiced'
    MANUALPAYMENT = 'Manual Payment'
    POLIPAYMENT = 'Poli Payment'
    STRIPEPAYMENT = 'Stripe Payment'
    PAYMENTCOMPLETED = 'Payment Completed'
    ALLOCATIONREVIEW = 'Allocation Review'
    ALLOCATIONPENDING = 'Allocation Pending'
    ALLOCATIONAPPROVED = 'Allocation Approved'
    ALLOCATIONCANCELLED = 'Allocation Cancelled'
    REFUNDREVIEW = 'Refund Review'
    REFUNDDONATED = 'Refund Donated'
    REFUNDREJECTED = 'Refund Rejected'
    REFUNDAPPROVED = 'Refund Approved'
    BOOKED = 'Booked'
    CANCELLED = 'Cancelled'

    REGISTRATION_STATUS_CHOICES = [
        (CREATED, _('Created')),
        (SUBMITTED, _('Submitted')),
        (INVOICED, _('Invoiced')),
        (MANUALPAYMENT, _('Manual Payment')),
        (POLIPAYMENT, _('Poli Payment')),
        (STRIPEPAYMENT, _('Stripe Payment')),
        (PAYMENTCOMPLETED, _('Payment Completed')),
        (ALLOCATIONREVIEW, _('Allocation Review')),
        (ALLOCATIONPENDING, _('Allocation Pending')),
        (ALLOCATIONAPPROVED, _('Allocation Approved')),
        (ALLOCATIONCANCELLED, _('Allocation Rejected')),
        (REFUNDREVIEW, _('Refund Review')),
        (REFUNDDONATED, _('Refund Donated')),
        (REFUNDREJECTED, _('Refund Rejected')),
        (REFUNDAPPROVED, _('Refund Approved')),
        (BOOKED, _('Booked')),
        (CANCELLED, _('Cancelled')),
    ]
    booking_status = FSMField(
        default=CREATED,
        verbose_name='Registration State',
        choices=REGISTRATION_STATUS_CHOICES,
        protected=False,
    )
    fair = models.ForeignKey(Fair, on_delete=models.CASCADE)
    stallholder = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # new
        on_delete=models.CASCADE
    )
    stall_manager_name = models.CharField(max_length=150)
    stall_category = models.ForeignKey(
        StallCategory,
        related_name='stall_registrations',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    stall_description = models.TextField()
    products_on_site = models.TextField()
    site_size = models.ForeignKey(
        InventoryItem,
        related_name='site_size_requirement',
        on_delete=models.SET_NULL,
        null=True
    )
    trestle_required = models.BooleanField(default=False)
    trestle_quantity = models.IntegerField(default=0)
    stall_shelter = models.TextField()
    power_required = models.BooleanField(default=False)
    total_charge = models.DecimalField(max_digits=8, decimal_places=2)
    selling_food = models.BooleanField(default=False)

    class Meta:
        verbose_name = "stallregistration"
        verbose_name_plural = "stallregistrations"

    def __str__(self):
        return self.booking_id

    def get_absolute_url(self):
        return reverse('stallregistration-detail', args=[str(self.id)])

    @property
    def booking_id(self):
        return self.id


class CommentType(models.Model):
    """
    Description of a Model to set Comment Types these types are used to make it easier for the Convener
    to identify comments for action, e.g. Site move request
    """
    type_name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.type_name

    class Meta:
        # sort comments in alphabetical order by default
        ordering = ('type_name',)
        verbose_name_plural = "CommentTypes"


class RegistrationComment(models.Model):
    """
    Description a model to capture stallholder and convener comments related to a Stall Registration instance.
    Convener comments can be made private so cannot be seen by Stallholders if required
    """
    stallholder = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # new
        null=True,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    comment_type = models.ForeignKey(
        CommentType,
        on_delete=models.CASCADE,
        null=True,
        related_name='comment_types'
    )
    comment = models.TextField(null=True)
    convener_only_comment = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='registration_comment_created_by',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    comment_parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    fair = models.ForeignKey(Fair, on_delete=models.CASCADE)
    is_done = models.BooleanField(default=False)

    class Meta:
        # sort comments in chronological order by default
        ordering = ('date_created',)

    def __str__(self):
        return 'Comment by {}'.format(str(self.created_by))


class FoodRegistration(models.Model):
    """
    Description: An extension of the StallRegistration model that captures via and one-to-one relationship the details
    regarding the food preparation / sale that is needed for the food licence application.
    """
    registration = models.OneToOneField(
        StallRegistration,
        related_name='food_registration',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    food_display_method = models.TextField()
    has_food_certificate = models.BooleanField(default=False)
    food_registration_certificate = models.FileField(upload_to='media/food_certificates')
    certificate_expiry_date = models.DateField(blank=True, null=True)
    food_fair_consumed = models.BooleanField(default=False)
    food_prep_equipment = models.ManyToManyField(
        FoodPrepEquipment,
        related_name='food_registration',
        through='FoodPrepEquipReq',
    )
    food_stall_type = models.ForeignKey(
        FoodSaleType,
        related_name='food_registration',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    food_source = models.TextField()
    food_storage_prep = models.TextField()
    has_food_prep = models.BooleanField(default=False)
    food_storage_prep_method = models.TextField()
    hygiene_methods = models.TextField()

    """
    Hooking the create_food_registration and save_food_registration methods to the StallRegistration model, whenever 
    a save event occurs and selling food has been selected. This kind of signal is called post_save.
    """

    @receiver(post_save, sender=StallRegistration)
    def create_food_registration(self, instance, created, **kwargs):
        if created and StallRegistration.selling_food:
            if created:
                FoodRegistration.objects.create(registration=instance)

    class Meta:
        verbose_name = "foodregistration"
        verbose_name_plural = "foodregistrations"


class FoodPrepEquipReq(models.Model):
    """
    Description a junction table joining FoodRegistration with FoodPrepEquipment used top capture whether the equipment
    is gas or electrical powered
    """
    ELECTRICAL = 'e'
    GAS = 'g'

    POWERED_CHOICE = [
        (ELECTRICAL, _('Electric Powered')),
        (GAS, _('Gas Powered'))
    ]
    food_registration = models.ForeignKey(
        FoodRegistration,
        on_delete=models.CASCADE,
        verbose_name='FoodPrepEquipmentRequired',
        related_name='food_prep_equip_req',
        blank=True,
        null=True
    )
    food_prep_equipment = models.ForeignKey(
        FoodPrepEquipment,
        on_delete=models.CASCADE,
        verbose_name='FoodPrepEquipment',
        related_name='food_prep_equip',
        blank=True,
        null=True
    )
    how_powered = models.CharField(
        choices=POWERED_CHOICE,
        max_length=11,
        default=ELECTRICAL,
    )

    """
    Hooking the create_food_prep_equip_req and save_food_prep_equip_req methods to the FoodRegistration model, whenever 
    a save event occurs. This kind of signal is called post_save.
    """

    @receiver(post_save, sender=FoodRegistration)
    def create_food_prep_equip_req(self, instance, created, **kwargs):
        if created:
            FoodPrepEquipReq.objects.create(food_registration=instance)

    class Meta:
        verbose_name = "foodprepequiprequired"
        verbose_name_plural = "foodprepequiprequirements"
