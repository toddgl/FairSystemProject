# utils/migrate_history.py

import os
import django
import pandas as pd
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from fairs.models import Site, SiteHistory
from accounts.models import CustomUser

history = pd.read_csv(
    '/usr/home/glenn/Documents/Rotary/Martinborough_Fair/Legacy_System/Extracts/sitehistory.csv')

# Open up a file to redirect print statements to for check outcomes
date = datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p")
dir_name = '//usr/home/glenn/Documents/Bin/Django/FairSystemProject//logs'
log_filename = f'historyextract_{date}'
suffix = '.txt'
with open(os.path.join(dir_name, log_filename + suffix), 'w') as f:
    # let's create some history
    for i, row in history.iterrows():
        # Check that the stallholder is in the database
        if CustomUser.objects.filter(reference_id=row['StallholderID']).exists():
            stallholder = CustomUser.objects.get(reference_id=row['StallholderID'])
            stallholderID = stallholder.pk
            # Check that the site exists
            if Site.objects.filter(site_name=row['CODE']).exists():
                site = Site.objects.get(site_name=row['CODE'])
                siteID = site.pk
                if SiteHistory.objects.filter(stallholder_id=stallholderID, year=row['Fair_Name'], site=siteID).exists():
                    print('SiteHistory for site {} and Stallholder ID {} and for the fair in {} was already created'.format(row['CODE'], stallholderID, row[ 'Fair_Name']), file=f)
                else:
                    SiteHistory.objects.create(
                        stallholder_id=stallholderID,
                        year=row['Fair_Name'],
                        site_id=siteID,
                        is_skipped=row['Skipped'],
                        number_events=row['NumEvents'],
                    )
                    print('Site history for Stallholder legacy reference {} for Site name {} and Fair Year {} has '
                          'been created'.format(row['StallholderID'], row['CODE'], row['Fair_Name']), file=f)
            else:
                print('Site name {} has not been created.'.format(row['CODE']), file=f)
        else:
            print('Stallholder legacy ID {} has not been created.'.format(row['StallholderID']), file=f)
