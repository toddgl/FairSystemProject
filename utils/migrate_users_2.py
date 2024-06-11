# utils/migrate_users_2.py

import os
import django
import pandas as pd
import phonenumbers as pn
from datetime import datetime
from django.db.utils import IntegrityError


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# we need to let Django handle the password hashing
from django.contrib.auth.hashers import make_password
from accounts.models import CustomUser, Profile

stallholders = pd.read_excel(
    '/usr/home/glenn/Documents/Rotary/Martinborough_Fair/Legacy_System/Extracts/Mar24/missing-stallholderlist2.xlsx')

# Open up a file to redirect print statements to for check outcomes
date = datetime.now(). strftime("%Y_%m_%d-%I:%M:%S_%p")
dir_name='//usr/home/glenn/Documents/Bin/Django/FairSystemProject/logs'
log_filename=f'userextract_{date}'
suffix = '.txt'

def generate_unique_username(base_username):
    username = base_username
    counter = 1
    while CustomUser.objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1
    return username

with open(os.path.join(dir_name, log_filename + suffix), 'w') as f:
    # let's create some users with default passwords equal to their username
    for index, row in stallholders.iterrows():
        tele_number = str(row['Tele']) if not pd.isnull(row['Tele']) else ''
        phone1 = ''
        phone2 = ''

        if tele_number:
            if '/' in tele_number:
                trimmed_number = tele_number[:tele_number.index('/')]
                phone1 = pn.format_number(pn.parse(trimmed_number, 'NZ'), pn.PhoneNumberFormat.NATIONAL)
                second_number = tele_number[tele_number.index('/') + 1:]
                phone2 = pn.format_number(pn.parse(second_number, 'NZ'), pn.PhoneNumberFormat.NATIONAL)
            else:
                phone1 = pn.format_number(pn.parse(tele_number, 'NZ'), pn.PhoneNumberFormat.NATIONAL)
        else:
            phone1 = ''
            phone2 = ''

        if CustomUser.objects.filter(reference_id=row['StallHolderID']).exists():
            print('Stallholder name {} with legacy ID {} already exists'.format(row['FNAME'], row['StallHolderID']), file=f)
        else:
            first_name = str(row['FNAME']).title() if not pd.isnull(row['FNAME']) else ''
            last_name = str(row['Surname']).title() if not pd.isnull(row['Surname']) else ''
            base_username = first_name[0] + last_name if first_name and last_name else ''

            username = generate_unique_username(base_username)

            try:
                CustomUser.objects.create(
                    reference_id=row['StallHolderID'],
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    email=row['EMAIL'],
                    phone=phone1,
                    password=make_password(first_name),
                    is_active=True,
                    is_staff=False,
                    role=3
                )
                print('Stallholder name {} with legacy ID {} has been created'.format(row['FNAME'].title(), row['StallHolderID']), file=f)

                createduser = CustomUser.objects.get(reference_id=row['StallHolderID'])
                if len(str(row['TradingName'])) > 0:
                    Profile.objects.filter(user=createduser.pk).update(org_name=str(row['TradingName']).title(), phone2=phone2)
                    print('Profile with user FK {} has been updated with the {} Stallholder business name.'.format(createduser.pk,
                                                                                                               str(row['TradingName']).title()), file=f)
            except IntegrityError as e:
                print(f"Error creating user for row {index}: {e}")