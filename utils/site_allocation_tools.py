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
    Site,
)

db_logger = logging.getLogger('db')


def site_allocation_emails():
    """
    Function to create stallholder emails to advise them that they have been pre-allocated a site based on their
    registration history asking them to apply for the fair before the activation date. The function is called from
    the management process dashboard . Processing information is recorded in the CustomDBLogger table which can be
    viewed using Django Admin
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
    df = pd.DataFrame.from_records(SiteHistory.fouryearhistorymgr.all().values())
    df['year'] = pd.to_datetime(df['year'], format='%Y')
    today = pd.to_datetime('today')
    begin = today - pd.offsets.Day(4 * 365)
    four_year_data = df[df['year'] > begin]

    events = Event.currenteventfiltermgr.all()
    count = 4

    while count > 0:
        group_counts = four_year_data.groupby(['stallholder_id', 'site_id']).size()

        if count == 1:
            year_sites = group_counts[group_counts == 1]
        else:
            year_sites = group_counts[group_counts >= 2]  # Prioritize sites with at least 2 occurrences

        # Sort stallholders by year count and then by the most recent year
        sorted_stallholders = []
        for stallholder_id in year_sites.index.get_level_values('stallholder_id').unique():
            stallholder_history = four_year_data[four_year_data['stallholder_id'] == stallholder_id]
            year_count = len(stallholder_history)
            latest_year = stallholder_history['year'].max()
            sorted_stallholders.append((stallholder_id, year_count, latest_year))

        sorted_stallholders.sort(key=lambda x: (x[1], x[2]), reverse=True)

        for stallholder_id, year_count, latest_year in sorted_stallholders:
            stallholder_history = four_year_data[four_year_data['stallholder_id'] == stallholder_id].copy()

            if count == 1:
                # Get the latest SiteHistory record for count=1
                recent_history = stallholder_history.sort_values(by='year', ascending=False).iloc[0]
                site_id = recent_history['site_id']
                is_half_size = recent_history['is_half_size']
                site_name = Site.objects.get(id=site_id).site_name

                # Debugging logs
                db_logger.warning(f'Processing site allocation for stallholder {stallholder_id} on site {site_name} ('
                                  f'count=1)', extra={'custom_category': 'site_allocation_debug'})

                required_site_size = 'Half Size Fair Site' if is_half_size else 'Full Size Fair Site'

                for event in events:
                    if EventSite.objects.filter(event_id=event.id, site_id=site_id,
                                                site__site_size__item_name=required_site_size).exists():
                        eventsite = EventSite.objects.get(event_id=event.id, site_id=site_id)
                        if not SiteAllocation.objects.filter(event_site__event__id=eventsite.event.id,
                                                             stallholder__id=stallholder_id).exists():
                            if eventsite.site_status == 1:
                                SiteAllocation.objects.create(
                                    stallholder_id=stallholder_id,
                                    event_site_id=eventsite.id,
                                    created_by_id=3,
                                )
                                eventsite.site_status = 2
                                eventsite.save()
                                db_logger.warning(f'Successfully allocated site {site_name} (size:'
                                                  f' {required_site_size}) to stallholder {stallholder_id}', extra={'custom_category': 'site_allocation_debug'})
                            else:
                                db_logger.warning(
                                    f'SiteAllocation for Stallholder ID {stallholder_id} Event Name {event.event_name} and '
                                    f'Site name {eventsite.site.site_name} has not been created, as the EventSite has been taken.',
                                    extra={'custom_category': 'Site Allocation'})
            else:
                # Separate historical count and recency checks
                stallholder_history['year_count'] = stallholder_history.groupby('site_id')['year'].transform('nunique')
                stallholder_history['max_year'] = stallholder_history.groupby('site_id')['year'].transform('max')

                # Sort by count and max_year
                sorted_history = stallholder_history.sort_values(by=['year_count', 'max_year'],
                                                                 ascending=[False, False])

                # Filter based on most recent occupancy first, then count
                preferred_history = sorted_history.groupby('stallholder_id').first().reset_index()
                preferred_history = preferred_history.sort_values(by=['max_year', 'year_count'],
                                                                  ascending=[False, False])

                # Select the preferred site based on the sorted history
                preferred_site_id = preferred_history.iloc[0]['site_id']

                site_histories = SiteHistory.objects.filter(stallholder_id=stallholder_id, site_id=preferred_site_id)
                recent_history = site_histories.order_by('-year').first()
                is_half_size = recent_history.is_half_size
                required_site_size = 'Half Size Fair Site' if is_half_size else 'Full Size Fair Site'
                site_name = Site.objects.get(id=preferred_site_id).site_name

                # Debugging logs
                db_logger.warning(f'Checking site {site_name} (size: {required_site_size}) for stallholder'
                                  f' {stallholder_id} (count={count})', extra={'custom_category': 'site_allocation_debug'})

                for event in events:
                    if EventSite.objects.filter(event_id=event.id, site_id=preferred_site_id,
                                                site__site_size__item_name=required_site_size).exists():
                        eventsite = EventSite.objects.get(event_id=event.id, site_id=preferred_site_id)
                        if not SiteAllocation.objects.filter(event_site__event__id=eventsite.event.id,
                                                             stallholder__id=stallholder_id).exists():
                            if eventsite.site_status == 1:
                                SiteAllocation.objects.create(
                                    stallholder_id=stallholder_id,
                                    event_site_id=eventsite.id,
                                    created_by_id=3,
                                )
                                eventsite.site_status = 2
                                eventsite.save()
                                db_logger.warning(f'Successfully allocated site {site_name} (size:'
                                                  f' {required_site_size}) to stallholder {stallholder_id}', extra={'custom_category': 'site_allocation_debug'})
                            else:
                                db_logger.warning(
                                    f'SiteAllocation for Stallholder ID {stallholder_id} Event Name {event.event_name} and '
                                    f'Site name {eventsite.site.site_name} has not been created, as the EventSite has been taken.',
                                    extra={'custom_category': 'Site Allocation'})
        count -= 1


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
