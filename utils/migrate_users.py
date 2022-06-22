# utils/migrate_users.py

import os
import django
import pandas as pd

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# we need to let Django handle the password hashing
from django.contrib.auth.hashers import make_password
from accounts.models import CustomUser, Profile

stallholders = pd.read_csv(
    '/usr/home/glenn/Documents/Rotary/Martinborough_Fair/Legacy_System/Extracts/stallholders.csv')

# let's create some users with default passwords equal to their username
for i, row in stallholders.iterrows():
    if CustomUser.objects.filter(reference_id=row['StallHolderID']).exists:
        print('Stallholder name {} with legacy ID {} already exists'.format(row['FirstName'], row['StallHolderID']))

    else:
        CustomUser.objects.create(
            reference_id=row['StallHolderID'],
            username=row['FirstName'],
            first_name=row['FirstName'],
            last_name=row['LastName'],
            email=row['Email'],
            phone=row['Phone'],
            password=make_password(row['FirstName']),
            role=3
        )
        print('Stallholder name {} with legacy ID {} has been created'.format(row['FirstName'], row['StallHolderID']))

        createduser = CustomUser.objects.get(reference_id=row['StallHolderID'])
        Profile.objects.filter(user=createduser.pk).update(org_name=row['BusinessName'])
        print('Profile with user FK {} has been updated with the {} Stallholder business name.'.format(createduser.pk,
                                                                                                       row['BusinessName']))
