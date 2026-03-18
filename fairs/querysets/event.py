# fairs/querysets/event.py

from django.db import models
from django.db.models import Case, When, F, DateField

class EventQuerySet(models.QuerySet):

    def active(self):
        return self.filter(is_cancelled=False)

    def with_actual_date(self):
        return self.annotate(
            actual_event_date=Case(
                When(
                    postponement_event_date__isnull=False,
                    then=F("postponement_event_date"),
                ),
                default=F("original_event_date"),
                output_field=DateField(),
            )
        ).order_by("actual_event_date")
