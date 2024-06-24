# foodlicence/models.pu

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import validate_email
from django_fsm import FSMField, transition
from registration.models import (
    FoodRegistration
)

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
    pdf_file = models.FileField(upload_to='pdfs/', null=True, blank=True)

class FoodLicence(models.Model):
    """
    Description: A model that records the creation and approval of Foodlicences requests that are passed to SWDC for
    consideration
    """
    CREATED = "Created"
    SUBMITTED = "Cancelled"
    REJECTED = "Rejected"
    APPROVED = "Approved"

    LICENCE_STATUS_CHOICES = [
        (CREATED, _("created")),
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
    date_completed = models.DateTimeField()
    food_licence_batch = models.ForeignKey(
        FoodLicenceBatch,
        on_delete=models.SET_NULL,
        related_name='food_licence_batch'
    )
    @transition(field=licence_status, source="Created", target="Submitted")
    def to_licence_status_submitted(self):
        pass

    @transition(field=licence_status, source="Submitted", target="Rejected")
    def to_licence_status_rejected(self):
        pass

    @transition(field=licence_status, source="Submitted", target="Approved")
    def to_licence_status_approved(self):
        pass
