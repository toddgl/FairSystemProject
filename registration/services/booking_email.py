# registration/services/booking_email.py

import logging

from django.conf import settings
from django.core.mail import send_mail

from emails.models import Email
from registration.models import CommentType

logger = logging.getLogger(__name__)


def send_booking_confirmation(registration):
    """
    Send booking confirmation and record the email history.
    """

    stallholder = registration.stallholder
    fair = registration.fair

    if not stallholder.email:
        logger.warning(
            "Booking confirmation not sent for registration %s: "
            "no email address.",
            registration.pk,
        )
        return False

    first_name = stallholder.first_name or "Stallholder"
    fair_year = fair.fair_year

    if registration.selling_food:
        subject = (
            f"{fair_year} Martinborough Fair - "
            "Hawkers Licence Approved"
        )

        body = (
            f"Thanks {first_name} your Hawkers Licence has been approved "
            f"by the South Wairarapa District Council and you should "
            f"have been sent to you. Your application for the "
            f"{fair_year} Fair is now at the status of Booked.\n\n"
            "Cheers\n"
            "Glenn Todd\n"
            "Martinborough Fair Stall Convener"
        )

    else:
        subject = (
            f"{fair_year} Martinborough Fair - Booking Confirmed"
        )

        body = (
            f"Thanks {first_name} for your prompt payment, "
            f"your application for the {fair_year} Fair "
            f"is now at the status of Booked.\n\n"
            "Cheers\n"
            "Glenn Todd\n"
            "Martinborough Fair Stall Convener"
        )

    sender = settings.DEFAULT_FROM_EMAIL
    recipient = stallholder.email

    # Find the CommentType representing booking confirmation.
    subject_type = CommentType.objects.get(
        type_name="Booking Status"
    )

    # Create history record BEFORE attempting delivery.
    email_history = Email.objects.create(
        stallholder=stallholder,
        fair=fair,
        subject_type=subject_type,
        from_email=sender,
        recipient=recipient,
        subject=subject,
        body=body,
        ok=False,
    )

    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=sender,
            recipient_list=[recipient],
            fail_silently=False,
        )

        email_history.ok = True
        email_history.save(update_fields=["ok"])

        logger.info(
            "Booking confirmation sent for registration %s",
            registration.pk,
        )

        return True

    except Exception:
        logger.exception(
            "Booking confirmation failed for registration %s",
            registration.pk,
        )

        # History remains with ok=False.
        return False