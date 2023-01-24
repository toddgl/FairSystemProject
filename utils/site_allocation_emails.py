# utils/site_allocation.py

import logging
from django.core.mail import EmailMultiAlternatives, BadHeaderError
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from smtplib import SMTPException
from fairs.models import (
    Fair,
    SiteAllocation,
)

db_logger = logging.getLogger('db')

current_fair = Fair.currentfairmgr.last()
site_allocations = SiteAllocation.currentallocationsmgr.all()
subject = "Martinborough Fair Site Registration - Action Required",
if site_allocations:
    for site_allocation in site_allocations:
        context = {'subject': subject, 'stallholder': site_allocation.stallholder, 'fair': current_fair}
        html_content = render_to_string("email/site_allocation_email.html", context)
        text_content = strip_tags(html_content)
        mail = EmailMultiAlternatives(
            subject =  subject,
            from_email = settings.EMAIL_HOST_USER,
            to = [site_allocation.stallholder.email],
            )
        mail.attach_alternative(html_content, "text/html")
        try:
            mail.send(fail_silently=False)
        except BadHeaderError:              # If mail's Subject is not properly formatted.
            db_logger.error('Invalid header found on ' + site_allocation.stallholder.email)
        except SMTPException as e:          # It will catch other errors related to SMTP.
            db_logger.exception ('There was an error sending an email.'+ e)