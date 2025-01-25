# emails/backend.py

from collections import defaultdict

from django.core.files.base import ContentFile

import logging

from accounts.models import CustomUser
from config import settings
from django.core.mail import EmailMultiAlternatives, BadHeaderError
from smtplib import SMTPException
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from collections import defaultdict

from .models import  Email

from fairs.models import (
    Fair
)
from registration.models import (
    StallRegistration,
    CommentType
)

db_logger = logging.getLogger('db')


def bulk_registration_emails(status, subject_type, body):
    """
    Function to send a single email to each stallholder who has the stall registration
    status passed in to the function.
    """
    # Query for stall registrations with the given status
    stall_registrations_qs = StallRegistration.registrationcurrentallmgr.filter(booking_status=status)
    current_fair = Fair.currentfairmgr.all().last()

    if stall_registrations_qs.exists():
        # Create a dictionary to store all site allocations by stallholder
        stallholder_dict = defaultdict(list)

        for stall_registration in stall_registrations_qs:
            stallholder_dict[stall_registration.stallholder].append(stall_registration)

        # Send a single email per stallholder
        for stallholder, registrations in stallholder_dict.items():
            try:
                # Retrieve the CommentType instance for the given subject_type
                subject_type_instance = CommentType.objects.get(type_name=subject_type)

                # Create email instance
                email = Email.objects.create(
                    subject_type=subject_type_instance,
                    fair=current_fair,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    stallholder=stallholder,
                    recipient=stallholder.email,
                    subject=f'Martinborough Fair {current_fair.fair_year} - {subject_type}',
                    body=body,
                )

            except CommentType.DoesNotExist:
                db_logger.error(f"CommentType with name '{subject_type}' does not exist.",
                    extra={'custom_category': 'Email'})
                continue

            except Exception as e:
                db_logger.error(f"Failed to save email to database (create): {e}",
                                extra={'custom_category': 'Email'})
                continue

            context = {
                'subject': f'Martinborough Fair {current_fair.fair_year} - {subject_type}',
                'body': body,
            }

            html_content = render_to_string("email/base_email.html", context)
            text_content = strip_tags(html_content)

            # Send the email
            mail = EmailMultiAlternatives(
                subject=strip_tags(subject_type),
                from_email=settings.EMAIL_HOST_USER,
                to=[stallholder.email],
            )
            mail.attach_alternative(html_content, "text/html")
            try:
                mail.send(fail_silently=False)
                # Update the `ok` field after successful send
                email.ok = True
                email.save(update_fields=['ok'])
            except BadHeaderError:
                db_logger.error(f'Invalid header found on {stallholder.email}',
                                extra={'custom_category': 'Email'})
            except SMTPException as e:
                db_logger.error(f'There was an error sending an email: {e}',
                                extra={'custom_category': 'Email'})
    else:
        db_logger.error(f'No stall registrations found for the given status: {subject_type}',
                        extra={'custom_category': 'Email'})


def single_registration_email(stallholder_id, subject_type, recipient, subject, body):
    '''
    Function to send an email to a single stallholder.
    Called from the convener_stall_registration_detail_view
    '''
    stallholder = CustomUser.objects.get(id=stallholder_id)
    current_fair = Fair.currentfairmgr.all().last()

    try:
        email = Email.objects.create(
            subject_type=subject_type,
            fair=current_fair,
            from_email=settings.DEFAULT_FROM_EMAIL,
            stallholder=stallholder,
            recipient=recipient,
            subject=subject,
            body=body,
        )
    except Exception as e:
        db_logger.error(f'Failed to save email to database (create) {e}',
                        extra={'custom_category': 'Email'}
                        )

    context = {
        'subject': subject,
        'body': body
    }

    html_content = render_to_string("email/base_email.html", context)
    text_content = strip_tags(html_content)
    mail = EmailMultiAlternatives(
        subject=strip_tags(subject),
        from_email=settings.EMAIL_HOST_USER,
        to=[recipient],
    )
    mail.attach_alternative(html_content, "text/html")
    try:
        mail.send(fail_silently=False)
        # Update the `ok` field after successful send
        email.ok = True
        email.save(update_fields=['ok'])
    except BadHeaderError:
        db_logger.error(f'Invalid header found on {stallholder.email}',
                        extra={'custom_category': 'Email'}
                        )
    except SMTPException as e:
        db_logger.error(f'There was an error sending an email. {e}',
                        extra={'custom_category': 'Email'}
                        )

