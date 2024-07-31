# utils/site_allocation_tools.py

import logging
import pandas as pd
from django.core.mail import EmailMultiAlternatives, BadHeaderError
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from smtplib import SMTPException
from fairs.models import (
    Fair,
    Event,
    EventSite,
    SiteAllocation,
    SiteHistory,

)

db_logger = logging.getLogger('db')

def site_allocation_emails():
    """
    Function to create stallholder emails to advise them that they have been preallocted a site based on their registration
    history asking them to apply for the fair before the activation date.
    The function is called from the management process dashboard . Processing information is recorded in the CustomDBLogger
    table which can be viewed using Django Admin
    """
    current_fair = Fair.currentfairmgr.last()
    site_allocations = SiteAllocation.currentallocationsmgr.all()
    subject = 'Martinborough Fair Site Registration - Action Required',
    if site_allocations:
        for site_allocation in site_allocations:
            context = {'subject': subject, 'stallholder': site_allocation.stallholder, 'fair': current_fair}
            html_content = render_to_string("email/site_allocation_email.html", context)
            text_content = strip_tags(html_content)
            mail = EmailMultiAlternatives(
                subject=strip_tags(subject),
                from_email=settings.EMAIL_HOST_USER,
                to=[site_allocation.stallholder.email],
            )
            mail.attach_alternative(html_content, "text/html")
            try:
                mail.send(fail_silently=False)
            except BadHeaderError:  # If mail's Subject is not properly formatted.
                db_logger.error('Invalid header found on ' + str(site_allocation.stallholder.email),
                                extra={'custom_category': 'Email'})
            except SMTPException as e:  # It will catch other errors related to SMTP.
                db_logger.error('There was an error sending an email.' + str(e), extra={'custom_category': 'Email'})


def site_allocations():
    """
    Function to create stallholder site allocations based on their historical registration site useages.
    The function is called from the management process dashboard and creates new instances in the SiteAllocation
    database table. processing information is recorded in the CustomDBLogger table which can be viewed using Django Admin
    """
    # Create a pandas dataframe(df) of the SiteHistory data

    df = pd.DataFrame.from_records(SiteHistory.fouryearhistorymgr.all().values())
    df['year'] = pd.to_datetime(df['year'], format='%Y')
    today = pd.to_datetime('today')
    begin = today - pd.offsets.Day(4 * 365)
    four_year_data = df[df['year'] > begin]
    """
    Create subset list where the stallholder has had the same site 4 years, 3 years and 2 years in row and finally 
    where the stallholder has only had a site a single time
    Process the stallholder site series for each current future event to create new SiteAllocation instances checking 
    to make sure that the EventSite site_status is set to Available this should be sufficient to prevent duplicates from 
    being created without resorting to test for duplicates before a save 
    """
    events = Event.currenteventfiltermgr.all()
    count = 4
    while count > 0:
        year_series = four_year_data.value_counts(subset=['stallholder_id', 'site_id']) == count
        year_sites = [i for i, j in year_series.items() if j == True]
        db_logger.info(str(count) + ' ' + str(year_sites), extra={'custom_category': 'Site Allocation'})
        for stallholder, site in year_sites:
            for event in events:
                if EventSite.objects.filter(event_id=event.id, site_id=site).exists():
                    eventsite = EventSite.objects.get(event_id=event.id, site_id=site)
                    if eventsite.site_status == 1:
                        SiteAllocation.objects.create(
                            stallholder_id=stallholder,
                            event_site_id=eventsite.id,
                            created_by_id=3,
                        )
                        eventsite.site_status = 2
                        eventsite.save()
                    else:
                        db_logger.warning('SiteAllocation for Stallholder ID ' + str(stallholder) + ' Event Name' + str(
                            event.event_name) + ' and Site name' + str(
                            eventsite.site.site_name) + 'has not been created, as the EventSite has been taken.',
                                          extra={'custom_category': 'Site Allocation'})
                else:
                    db_logger.warning('SiteAllocation for Stallholder ID ' + str(stallholder) + ' Event Name' + str(
                        event.event_name) + ' and Site name' + str(
                        eventsite.site.site_name) + 'has not been created, as the EventSite does not exist.',
                                      extra={'custom_category': 'Site Allocation'})
        count = count - 1

def delete_unregistered_allocations():
    """
    Function to delete stallholder site allocations that have not been associated with a registration record.
    The function is called from the management process dashboard and removes records from the SiteAllocation
    database table. It will not remove record that are assocciated with a registration, or if the record has its on_hold flag set.
    processing information is recorded in the CustomDBLogger table which can be viewed using Django Admin
    """
    unregistered_allocations = SiteAllocation.objects.filter(stall_registration__isnull=True, on_hold=False)
    if unregistered_allocations:
        for allocation in unregistered_allocations:
            eventsite = allocation.event_site
            eventsite.site_status = 1
            try:
                allocation.delete()
                eventsite.save()
            except Exception as e:          # It will catch other errors related to the delete call.
                db_logger.error('There was an error deleting the unregistered site allocations.'+ e,  extra={'custom_category':'Site Allocations'})



