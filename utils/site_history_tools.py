# utils/site_history_tools.py

import logging
from django.db.models import Count
from fairs.models import (
    Fair,
    SiteAllocation,
    SiteHistory,
    InventoryItem,
)

db_logger = logging.getLogger('db')

def populate_site_history():
    """
    Populates the SiteHistory model based on StallRegistration and SiteAllocation data.
    Ensures no duplicates and updates existing records if necessary.
    """

    current_fair_year = Fair.currentfairmgr.first().fair_year

    # Aggregate SiteAllocations to count events per site for each stallholder
    site_allocations = (
        SiteAllocation.objects
        .filter(stall_registration__booking_status='Booked')  # Only include registrations with status 'Booked'
        .values('stallholder', 'event_site__site', 'stall_registration__site_size')
        .annotate(number_events=Count('event_site__event', distinct=True))
    )

    # Track existing SiteHistory entries to identify those needing removal
    existing_site_histories = SiteHistory.objects.values('id', 'stallholder_id', 'site_id', 'year')
    existing_site_history_map = {
        (entry['stallholder_id'], entry['site_id'], entry['year']): entry['id']
        for entry in existing_site_histories
    }

    processed_entries = set()

    for allocation in site_allocations:
        stallholder_id = allocation['stallholder']
        site_id = allocation['event_site__site']
        site_size_id = allocation['stall_registration__site_size']
        number_events = allocation['number_events']
        year = current_fair_year


        # Retrieve the `InventoryItem` object if `site_size_id` is not null
        site_size = None
        if site_size_id:
            try:
                site_size = InventoryItem.objects.get(id=site_size_id)
            except InventoryItem.DoesNotExist:
                db_logger.error(
                    f'There was an error with the site history.  InventoryItem with ID {site_size_id} does not exist. Skipping.',
                    extra={'custom_category': 'Site History'}
                )

        # Determine if the site size is half-size (or other conditions)
        if site_size:
            if site_size.item_name == 'Half Size Fair Site':
                is_half_size = True
            else:
                is_half_size = False
        else:
            is_half_size = False

        # Mark this entry as processed
        processed_entries.add((stallholder_id, site_id, year))

        # Check if a SiteHistory entry exists for this stallholder and site
        site_history, created = SiteHistory.objects.update_or_create(
            stallholder_id=stallholder_id,
            site_id=site_id,
            year=year,
            defaults={
                'site_size_id': site_size_id,
                'number_events': number_events,
                'is_half_size': is_half_size,
                # Add additional fields to update if necessary
            }
        )

    # Remove outdated SiteHistory entries for the current year only
    for (stallholder_id, site_id, year), site_history_id in existing_site_history_map.items():
        if year == current_fair_year and (stallholder_id, site_id, year) not in processed_entries:
            SiteHistory.objects.filter(id=site_history_id).delete()


