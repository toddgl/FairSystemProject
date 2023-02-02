# utils/site_allocation.py

import os
import django
import logging
import pandas as pd
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from fairs.models import SiteHistory, Event, EventSite, SiteAllocation

#Set up db logger

db_logger = logging.getLogger('db')

# Create a pandas dataframe(df) of the SiteHistory data

df = pd.DataFrame.from_records(SiteHistory.objects.all().values())
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
for event in events:
    count = 4
    while count > 0:
        year_series = four_year_data.value_counts(subset=['stallholder_id', 'site_id']) == count
        year_sites = [i for i, j in year_series.items() if j == True]
        db_logger.info(str(count) + ' ' +str(year_sites), extra={'custom_category':'Site Allocation'} )
        for stallholder, site in year_sites:
            if EventSite.objects.filter(event_id=event.id, site_id=site).exists():
                eventsite = EventSite.objects.get(event_id=event.id, site_id=site)
                if eventsite.site_status == 1:
                    SiteAllocation.objects.create(
                        stallholder_id=stallholder,
                        event_site_id=eventsite.id,
                        created_by_id=3,
                    )
                else:
                    db_logger.warning('SiteAllocation for Stallholder ID ' + str(stallholder) + ' Event Name' + str(
                        event.event_name) + ' and Site name' + str(
                        eventsite.site.site_name) + 'has not been created, as the EventSite was not Available.',
                                      extra={'custom_category': 'Site Allocation'})
            else:
                db_logger.warning('SiteAllocation for Stallholder ID ' + str(stallholder) + ' Event Name' + str(
                    event.event_name) + ' and Site name' + str(
                    eventsite.site.site_name) + 'has not been created, as the EventSite was not Available.',
                          extra={'custom_category': 'Site Allocation'})
        count = count - 1
