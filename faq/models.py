# faq/models.py
from django.db import models
from fairs.models import (
    Location,
)


# Create your models here.

class FAQ(models.Model):
    """
    Stpre for the fair referenced by location
    """
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




