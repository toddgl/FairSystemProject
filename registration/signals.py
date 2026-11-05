# registration/signals.py

import logging

from django.db import transaction
from django.dispatch import receiver

from django_fsm.signals import post_transition

from registration.models import StallRegistration
from registration.services.booking_email import send_booking_confirmation
from registration.services.invoice_email import send_invoice_notification

logger = logging.getLogger(__name__)

@receiver(
    post_transition,
    sender=StallRegistration,
    dispatch_uid="stallregistration_invoice_notification",
)
def stallregistration_invoice_notification(
    sender,
    instance,
    name,
    source,
    target,
    **kwargs,
):
    """
    Send invoice notification when a registration
    transitions to Invoiced.
    """

    if name != "to_booking_status_invoiced":
        return

    if target != StallRegistration.INVOICED:
        return

    transaction.on_commit(
        lambda: send_invoice_notification(instance)
    )


@receiver(
    post_transition,
    sender=StallRegistration,
    dispatch_uid="stallregistration_booking_confirmation",
)
def stallregistration_booking_confirmation(
    sender,
    instance,
    name,
    source,
    target,
    **kwargs,
):
    """
    Send booking confirmation when a registration transitions
    from Payment Completed to Booked.
    """

    # Only respond to the actual Booked transition.
    if name != "to_booking_status_booked":
        return

    if target != StallRegistration.BOOKED:
        return

    # Schedule email after the database transaction commits.
    transaction.on_commit(
        lambda: send_booking_confirmation(instance)
    )