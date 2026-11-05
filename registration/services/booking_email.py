# registration/services/booking_email.py

import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def send_booking_confirmation(registration):
    """
    Send the appropriate booking confirmation email
    when a StallRegistration becomes Booked.
    """

    stallholder = registration.stallholder

    if not stallholder.email:
        logger.warning(
            "Booking confirmation not sent for registration %s: "
            "stallholder has no email address.",
            registration.pk,
        )
        return

    first_name = stallholder.first_name or "Stallholder"

    # Get the Fair year from the registration's associated Fair.
    fair_year = registration.fair.fair_year

    if registration.selling_food:
        subject = f"{fair_year} Martinborough Fair - Hawkers Licence Approved"

        message = (
            f"Thanks {first_name} your Hawkers Licence has been approved "
            f"by the South Wairarapa District Council and you should "
            f"have been sent to you. Your application for the "
            f"{fair_year} Fair is now at the status of Booked.\n\n"
            "Cheers\n"
            "Glenn Todd\n"
            "Martinborough Fair Stall Convener"
        )

    else:
        subject = f"{fair_year} Martinborough Fair - Booking Confirmed"

        message = (
            f"Thanks {first_name} for your prompt payment, "
            f"your application for the {fair_year} Fair "
            f"is now at the status of Booked.\n\n"
            "Cheers\n"
            "Glenn Todd\n"
            "Martinborough Fair Stall Convener"
        )

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[stallholder.email],
            fail_silently=False,
        )

        logger.info(
            "Booking confirmation email sent for registration %s "
            "to %s",
            registration.pk,
            stallholder.email,
        )

    except Exception:
        logger.exception(
            "Failed to send booking confirmation for registration %s",
            registration.pk,
        )