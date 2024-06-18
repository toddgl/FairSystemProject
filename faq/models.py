# faq/models.py

from django.utils.translation import gettext_lazy as _
from django.db import models
from fairs.models import (
    Location,
)


# Create your models here.
class ActiveFaqManager(models.Manager):
    """
    Manager that returns the current Faqs, accessed by calling
    Faq.activefaqrmgr.all()
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True).order_by('category')

class FAQCategory(models.Model):
    """
    Model to represent FAQ categories
    """
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class FAQ(models.Model):
    """
    Stpre for the fair FAQ's referenced by location
    """
    category = models.ForeignKey(FAQCategory, default='Shopping', on_delete=models.CASCADE)
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

    objects = models.Manager()
    activefaqmgr = ActiveFaqManager()

    def __str__(self):
        return self.question

    class Meta:
        verbose_name_plural = "FAQs"




