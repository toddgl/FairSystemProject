# utils/migrate_sites.py

import os
import django
import pandas as pd

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from fairs.models import Site, Event, EventSite, Zone

sites = pd.read_csv(
    '/usr/home/glenn/Documents/Rotary/Martinborough_Fair/Legacy_System/Extracts/sites.csv')

# let's create some sites
for i, row in sites.iterrows():
    if Zone.objects.filter(zone_code=row['Zone']).exists():
        zone = Zone.objects.get(zone_code=row['Zone'])
        zoneID = zone.pk
        if Site.objects.filter(site_name=row['Site']).exists():
            print('Site name {} for Zone {} already exists'.format(row['Site'], row['Zone']))

        else:
            Site.objects.create(
                zone_id=zoneID,
                site_name=row['Site'],
                site_size_id=int(row['Size']),
                created_by_id=3,
            )
            print('Site name {} for Zone{} has been created'.format(row['Site'], row['Zone']))
            created_site = Site.objects.get(site_name=row['Site'])

            """
            Create the event site relationship with the just created site and all future events
            """
            events = Event.filtermgr.all()
            objs = [
                EventSite(
                    event=event,
                    site=created_site,
                    site_status=1,
                )
                for event in events
            ]
            EventSite.objects.bulk_create(objs)

    else:
        print('Zone name {} has not been created.'.format(row['Zone']))
