# registration/model.py

import datetime
from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.conf import settings  # new
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django_fsm import FSMField, transition

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
    CREATED = 1
    SUBMITTED = 2
    INVOICED = 3
    MANUALPAYMENT = 4
    POLIPAYMENT = 5
    STRIPEPAYMENT = 6
    PAYMENTCOMPLETED = 7
    ALLOCATIONREVIEW = 8
    ALLOCATIONPENDING = 9
    ALLOCATIONAPPROVED = 10
    ALLOCATIONREJECTED = 11
    REFUNDREVIEW = 12
    REFUNDDONATED = 13
    REFUNDREJECTED = 14
    REFUNDAPPROVED = 15
    BOOKED = 16
    CANCELLED = 17

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
        (ALLOCATIONREJECTED, _('Allocation Rejected')),
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
        protected=True,
    )
    event_site = models.ForeignKey(
        'fairs.EventSite',
        verbose_name='eventsite',
        related_name='stall_registrations',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
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
    trestle_required = models.BooleanField(default=False)
    trestle_quantity = models.IntegerField(default=0)
    stall_shelter = models.TextField()
    power_required = models.BooleanField(default=False)
    event_power = models.ForeignKey(
        'fairs.EventPower',
        verbose_name='eventpower',
        related_name='stall_registrations',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    total_charge = models.DecimalField(max_digits=8, decimal_places=2)
    selling_food = models.BooleanField(default=False)

    @property
    def booking_id(self):
        return self.id

    def __str__(self):
        return self.booking_id

    class Meta:
        verbose_name_plural = "StallRegistrations"
