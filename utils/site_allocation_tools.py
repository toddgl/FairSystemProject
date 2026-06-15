# utils/site_allocation_tools.py

import logging
import pandas as pd
from django.core.mail import EmailMultiAlternatives, BadHeaderError
from django.conf import settings
from collections import defaultdict
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from smtplib import SMTPException
from fairs.models import (
    Fair,
    Event,
    EventSite,
    SiteAllocation,
    SiteHistory,
    Site,
)

from utils.services.site_allocation_service import (
    SiteAllocationService,
)

db_logger = logging.getLogger('db')

def site_allocation_emails():
    """
    Function to send a single email to each stallholder who has one or more site allocations,
    advising them to apply for the fair before the activation date.
    """
    current_fair = Fair.currentfairmgr.last()
    site_allocations = SiteAllocation.currentallocationsmgr.all()
    subject = 'Martinborough Fair Site Registration - Action Required'

    if site_allocations:
        # Create a dictionary to store all site allocations by stallholder
        stallholder_allocations = defaultdict(list)

        for site_allocation in site_allocations:
            stallholder_allocations[site_allocation.stallholder].append(site_allocation)

        # Send a single email per stallholder
        for stallholder, allocations in stallholder_allocations.items():
            context = {
                'subject': subject,
                'stallholder': stallholder,
                'fair': current_fair,
                'allocations': allocations  # Pass all site allocations for the stallholder
            }
            html_content = render_to_string("email/site_allocation_email.html", context)
            text_content = strip_tags(html_content)
            mail = EmailMultiAlternatives(
                subject=strip_tags(subject),
                from_email=settings.EMAIL_HOST_USER,
                to=[stallholder.email],
            )
            mail.attach_alternative(html_content, "text/html")
            try:
                mail.send(fail_silently=False)
            except BadHeaderError:
                db_logger.error('Invalid header found on ' + str(stallholder.email),
                                extra={'custom_category': 'Email'})
            except SMTPException as e:
                db_logger.error('There was an error sending an email.' + str(e), extra={'custom_category': 'Email'})

def site_allocations():
    SiteAllocationService.allocate_sites()


def delete_unregistered_allocations():
    """
    Function to delete stallholder site allocations that have not been associated with a registration record. The
    function is called from the management process dashboard and removes records from the SiteAllocation database
table. It will not remove record that are associated with a registration, or if the record has its on_hold flag
set. processing information is recorded in the CustomDBLogger table which can be viewed using Django Admin
"""
    unregistered_allocations = SiteAllocation.objects.filter(stall_registration__isnull=True, on_hold=False)
    if unregistered_allocations:
        for allocation in unregistered_allocations:
            eventsite = allocation.event_site
            eventsite.site_status = 1
            try:
                allocation.delete()
                eventsite.save()
            except Exception as e:  # It will catch other errors related to the delete call.
                db_logger.error('There was an error deleting the unregistered site allocations.' + e,
                                extra={'custom_category': 'Site Allocations'})
