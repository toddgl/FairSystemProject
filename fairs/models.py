# fairs/model.py

from django.db import models
from django.utils import timezone


# Create your models here.

class Fair(models.Model):
    """
    Description: Stores the details of each fair instance
    Usesa CharField for fair_year because we are going to convert
    that value to string for converting it to python datetime object.
    """

    fair_year = models.CharField(max_length=4, default='2022')
    fair_name = models.CharField(max_length=40)
    date_created = models.DateTimeField(default=timezone.now)
    date_cancelled = models.DateTimeField(blank=True, default=None, null=True)
    fair_description = models.TextField()
    is_cancelled = models.BooleanField(default=False)
    activation_date = models.DateTimeField(blank=True, default=None, null=True)
    is_activated = models.BooleanField(default=False)

    def __str__(self):
        return fair_name

    class Meta:
        verbose_name_plural = "Fairs"

    @property
    def get_fair_year(self):
        """
        Format it to datetime object. You need to convert `year`
        to str if it is `IntergerField`. ex: str(self.year).
        """
        date = timezone.datetime.strptime('%Y', self.fair_year)
        return date


class Event(models.Model):
    """
    Description: Stores the details of events associated with fair
    """
    event_name = models.CharField(max_length=40)
    original_event_date = models.DateTimeField()
    postponement_event_date = models.DateTimeField(blank=True, default=None, null=True)
    date_created = models.DateTimeField(default=timezone.now)
    date_cancelled = models.DateTimeField(blank=True, default=None, null=True)
    event_description = models.TextField()
    is_cancelled = models.BooleanField(default=False)
    is_postponed = models.BooleanField(default=False)
    fair = models.ForeignKey(Fair, on_delete=models.CASCADE)

    def __str__(self):
        return event_name

    class Meta:
        verbose_name_plural = "Events"
