# utils/site_allocation.py

import os
import django
import pandas as pd
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from fairs.models import SiteHistory, Event, EventSite, SiteAllocation

"""
Create a pandas dataframe(df) of the SiteHistory data
"""
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
count = 4
events = Event.currenteventfiltermgr.all()
# Open up a file to redirect print statements to for check outcomes
date = datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p")
dir_name = '//usr/home/glenn/Documents/Bin/Django/FairSystemProject//logs'
log_filename = f'siteallocation{date}'
suffix = '.txt'
with open(os.path.join(dir_name, log_filename + suffix), 'w') as f:
    for event in events:
        while count > 0:
            year_series = four_year_data.value_counts(subset=['stallholder_id', 'site_id']) == count
            year_sites = [i for i, j in year_series.items() if j == True]
            print(count, year_sites, file=f)
            for stallholder, site in year_sites:
                eventsite = EventSite.objects.get(event_id=event.id, site_id=site)
                if eventsite.site_status == 1:
                    SiteAllocation.objects.create(
                        stallholder_id=stallholder,
                        event_site_id=eventsite.id,
                        created_by_id=3,
                    )
                    print('SiteAllocation for Stallholder ID {} Event Name {} and Site name {} has been '
                          'created'.format(stallholder, event.event_name, eventsite.site.site_name), file=f)
                else:
                    print('SiteAllocation for Stallholder ID {} Event Name {} and Site name {} has not been created, '
                          'the EventSite was not Available'.format(stallholder, event.event_name,
                                                                   eventsite.site.site_name), file=f)
            count = count - 1
