# fairs/querysets/event.py

from django.db.models import Case, When, F, DateField
from django.db import models
from django.db.models.functions import Coalesce
from django.utils import timezone


class EventQuerySet(models.QuerySet):
    def active(self):
        """Filters out cancelled events."""
        return self.filter(is_cancelled=False)

    def with_actual_date(self):
        """
        Annotates each event with 'actual_event_date'.
        Uses 'postponement_event_date' if available, otherwise 'original_event_date'.
        """
        return self.annotate(
            actual_event_date=Coalesce(
                'postponement_event_date',
                'original_event_date',
                output_field=models.DateField()
            )
        )

    def upcoming(self):
        """
        Filters events scheduled on or after today based on their actual date.
        Requires with_actual_date() to be chained or called internally.
        """
        today = timezone.now().date()
        return self.with_actual_date().filter(actual_event_date__gte=today)

    def past(self):
        """Filters events that occurred before today."""
        today = timezone.now().date()
        return self.with_actual_date().filter(actual_event_date__lt=today)

