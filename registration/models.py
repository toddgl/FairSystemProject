# registration/model.py

import datetime
from django.db import models
from django.utils import timezone
from django.urls import reverse
from accounts.models import CustomUser
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

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
        CustomUser,
        related_name='food_prep_equipment_created_by',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    updated_by = models.ForeignKey(
        CustomUser,
        related_name='food_prep_equipment_updated_by',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    def __str__(self):
        return self.equipment_name

    class Meta:
        verbose_name_plural = "FoodPrepEquipments"

