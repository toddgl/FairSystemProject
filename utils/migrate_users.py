# utils/migrate_users.py

import os
import django
import pandas as pd
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# we need to let Django handle the password hashing
from django.contrib.auth.hashers import make_password
from accounts.models import CustomUser, Profile

stallholders = pd.read_csv(
    '/usr/home/glenn/Documents/Rotary/Martinborough_Fair/Legacy_System/Extracts/stallholders.csv')

# Open up a file to redirect print statements to for check outcomes
date = datetime.now(). strftime("%Y_%m_%d-%I:%M:%S_%p")
dir_name='//usr/home/glenn/Documents/Bin/Django/FairSystemProject//logs'
log_filename=f'userextract_{date}'
suffix = '.txt'

with open(os.path.join(dir_name, log_filename + suffix), 'w') as f:
    # let's create some users with default passwords equal to their username
    for i, row in stallholders.iterrows():
        if CustomUser.objects.filter(reference_id=row['StallHolderID']).exists():
            print('Stallholder name {} with legacy ID {} already exists'.format(row['FirstName'], row['StallHolderID']), file=f)

        else:
            CustomUser.objects.create(
                reference_id=row['StallHolderID'],
                username=row['UserName'],
                first_name=row['FirstName'],
                last_name=row['LastName'],
                email=row['Email'],
                phone=row['Phone'],
                password=make_password(row['FirstName']),
                role=3
            )
            print('Stallholder name {} with legacy ID {} has been created'.format(row['FirstName'], row['StallHolderID']), file=f)

            createduser = CustomUser.objects.get(reference_id=row['StallHolderID'])
            if len(row['BusinessName']) > 0:
                Profile.objects.filter(user=createduser.pk).update(org_name=row['BusinessName'])
                print('Profile with user FK {} has been updated with the {} Stallholder business name.'.format(createduser.pk,
                                                                                                           row['BusinessName']), file=f)
