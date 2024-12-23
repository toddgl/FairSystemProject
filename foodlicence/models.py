# foodlicence/models.py

import datetime
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import validate_email
from django_fsm import FSMField, transition
from registration.models import (
    FoodRegistration
)

current_year = datetime.datetime.now().year
next_year = current_year + 1


class FoodLicenceBatchCurrentManager(models.Manager):
    """
    Description: Methods to access current FoodLicencBbatch instances
    """
    def get_queryset(self):
        current_year = datetime.datetime.now().year
        next_year = current_year + 1
        return super().get_queryset().filter(date_created__year__in=[current_year, next_year])

class FoodLicenceBatch(models.Model):
    """
    Description: A Model to record the batches of Foodlicence Requests that are passed to the SWDC for consideration
    and approval
    """
    recipient_email = models.EmailField(validators=[validate_email])
    date_created = models.DateTimeField(auto_now_add=True)
    date_sent = models.DateTimeField()
    date_returned = models.DateTimeField(null=True, blank=True)
    date_closed = models.DateTimeField(null=True, blank=True)
    batch_count = models.IntegerField()
    pdf_file = models.FileField(upload_to='pdfs/' + str(current_year), null=True, blank=True)

    objects = models.Manager()
    foodlicencebatchcurrentmgr = FoodLicenceBatchCurrentManager()

class FoodLicenceCurrentManager(models.Manager):
    """
    Description: Methods to access current FoodLicences
    """

    def get_queryset(self):
        return super().get_queryset().filter(food_registration__registration__fair__fair_year__in=[current_year,
                                                                                                next_year],
                                             food_registration__registration__fair__is_activated=True)

    def get_created(self):
        return self.get_queryset().filter(licence_status="Created")

    def get_staged(self):
        return self.get_queryset().filter(licence_status="Staged")

    def get_batched(self):
        return self.get_queryset().filter(licence_status="Batched")

    def get_submitted(self):
        return self.get_queryset().filter(licence_status="Submitted")

    def get_rejected(self):
        return self.get_queryset().filter(licence_status="Rejected")

    def get_approved(self):
        return self.get_queryset().filter(licence_status="Approved")

class FoodLicence(models.Model):
    """
    Description: A model that records the creation and approval of Foodlicences requests that are passed to SWDC for
    consideration
    """
    CREATED = "Created"
    STAGED = "Staged"
    BATCHED = "Batched"
    SUBMITTED = "Submitted"
    REJECTED = "Rejected"
    APPROVED = "Approved"

    LICENCE_STATUS_CHOICES = [
        (CREATED, _("created")),
        (STAGED, _("staged")),
        (BATCHED, _('batched')),
        (SUBMITTED, _("submitted")),
        (REJECTED, _("rejected")),
        (APPROVED, _("approved")),
    ]
    licence_status = FSMField(
        default=CREATED,
        verbose_name='Food Licence State',
        choices=LICENCE_STATUS_CHOICES,
        protected=False,
    )
    food_registration = models.ForeignKey(
        FoodRegistration,
        on_delete=models.CASCADE,
        related_name='food_licence'
    )
    date_requested = models.DateTimeField(auto_now_add=True)
    date_completed = models.DateTimeField(blank=True, null=True)
    food_licence_batch = models.ForeignKey(
        FoodLicenceBatch,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='food_licence_batch'
    )
    objects = models.Manager()
    foodlicencecurrentmgr = FoodLicenceCurrentManager()

    @transition(field=licence_status, source="Created", target="Staged")
    def to_licence_status_staged(self):
        pass

    @transition(field=licence_status, source="Staged", target="Batched")
    def to_licence_status_batched(self):
        pass

    @transition(field=licence_status, source="Batched", target="Submitted")
    def to_licence_status_submitted(self):
        pass

    @transition(field=licence_status, source="Submitted", target="Rejected")
    def to_licence_status_rejected(self):
        pass

    @transition(field=licence_status, source="Submitted", target="Approved")
    def to_licence_status_approved(self):
        pass
