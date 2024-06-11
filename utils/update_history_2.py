# utils/update_history_2.py

import os
import django
import pandas as pd
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from fairs.models import Site, SiteHistory
from accounts.models import CustomUser

history = pd.read_excel('/usr/home/glenn/Documents/Rotary/Martinborough_Fair/Legacy_System/Extracts/Mar24/dvpdata-sitehistory-2019-2024.xlsx')

# Open up a file to redirect print statements to for check outcomes
date = datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p")
dir_name = '//usr/home/glenn/Documents/Bin/Django/FairSystemProject//logs'
log_filename = f'historyupdate_{date}'
suffix = '.txt'
with open(os.path.join(dir_name, log_filename + suffix), 'w') as f:
    # let's create some history
    for i, row in history.iterrows():
        # Check that the stallholder is in the database
        if CustomUser.objects.filter(reference_id=row['StallHolderID']).exists():
            stallholder = CustomUser.objects.get(reference_id=row['StallHolderID'])
            stallholderID = stallholder.pk
            # Check that the site exists
            if Site.objects.filter(site_name=row['CODE']).exists():
                site = Site.objects.get(site_name=row['CODE'])
                siteID = site.pk
                if SiteHistory.objects.filter(stallholder_id=stallholderID, year=row['Fair_Name'], site=siteID).exists():
                    SiteHistory.objects.filter(stallholder_id=stallholderID, year=row['Fair_Name'], site=siteID).update(is_half_size=row['bIsHalfSite'])

                    print('Site history for Stallholder legacy reference {} for Site name {} and Fair Year {} has '
                          'been updated to show if it was a half size site {}'.format(row['StallHolderID'],
                                                                                      row['CODE'], row['Fair_Name'], row['bIsHalfSite']), file=f)
            else:
                print('Site name {} does not exist.'.format(row['CODE']), file=f)
        else:
            print('Stallholder legacy ID {} does not exist.'.format(row['StallHolderID']), file=f)
