# faq/models.py

from django.utils.translation import gettext_lazy as _
from django.db import models
from fairs.models import (
    Location,
)


# Create your models here.

class FAQ(models.Model):
    """
    Stpre for the fair FAQ's referenced by location
    """
    SHOPPING = 1
    LOGGING_IN = 2
    APPLICATIONS = 3
    ON_THE_DAY = 4
    FOOD_STALLS = 5
    BUSKERS = 6

    CATEGORY_CHOICE = [
        (SHOPPING, _('Shopping')),
        (LOGGING_IN, _('Logging In')),
        (APPLICATIONS, _('Applications')),
        (ON_THE_DAY, _('On the Day')),
        (FOOD_STALLS, _('Food Stalls')),
        (BUSKERS, _('Buskers'))
    ]

    category = models.PositiveSmallIntegerField(
        choices=CATEGORY_CHOICE,
        default=SHOPPING
    )
    location = models.ForeignKey(
        Location,
        related_name='faq_location',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    question = models.TextField()
    answer = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.question

    class Meta:
        verbose_name_plural = "FAQs"




