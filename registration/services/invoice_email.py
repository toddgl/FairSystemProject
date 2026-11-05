# registration/services/invoice_email.py

import logging

from django.conf import settings
from django.core.mail import send_mail

from emails.models import Email
from registration.models import CommentType

logger = logging.getLogger(__name__)


def send_invoice_notification(registration):
    """
    Send invoice notification to a stallholder and record
    the email in Email history.
    """

    stallholder = registration.stallholder
    fair = registration.fair

    if not stallholder.email:
        logger.warning(
            "Invoice notification not sent for registration %s: "
            "stallholder has no email address.",
            registration.pk,
        True)
        return False

    first_name = stallholder.first_name or "Stallholder"

    # Retrieve allocations belonging to this registration.
    allocations = (
        registration.site_allocation
        .select_related(
            "event_site__event",
            "event_site__site",
        )
        .order_by(
            "event_site__event__event_name",
            "event_site__site",
        )
    )

    allocation_lines = []

    for allocation in allocations:
        event_name = allocation.event_site.event.event_name
        site_name = str(allocation.event_site.site)

        # Avoid appending "Event" twice.
        if not event_name.lower().endswith("event"):
            event_name = f"{event_name} Event"

        allocation_lines.append(
            f"- {event_name} - {site_name}"
        )

    if allocation_lines:
        allocation_text = "\n".join(allocation_lines)
    else:
        allocation_text = "- No site allocations recorded"

    subject = (
        f"{fair.fair_year} Martinborough Fair - "
        f"Invoice Generated - Application {registration.pk}"
    )

    body = (
        f"Hi {first_name}\n\n"
        f"You have been allocated the following sites "
        f"for your application number {registration.pk}\n\n"
        f"{allocation_text}\n\n"
        f"Your Martinborough Fair application has had the "
        f"invoice generated. If you haven't already done so, "
        f"please log into the system and click on the "
        f"\"Pay amount owed\" button to be taken to a secure "
        f"payment portal where you can pay via credit card. "
        f"If you have any issues or want changes use the "
        f"comments functionality to outline the details.\n\n"
        f"Cheers\n"
        f"Glenn Todd\n"
        f"Martinborough Fair Stall Convener"
    )

    sender = settings.DEFAULT_FROM_EMAIL
    recipient = stallholder.email

    subject_type = CommentType.objects.get(
        type_name="Invoicing"
    )

    # Record email history before attempting delivery.
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
            "Invoice notification sent for registration %s",
            registration.pk,
        )

        return True

    except Exception:
        logger.exception(
            "Invoice notification failed for registration %s",
            registration.pk,
        )
        return False
