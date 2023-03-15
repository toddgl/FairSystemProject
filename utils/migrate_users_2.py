# utils/migrate_users_2.py

import os
import django
import pandas as pd
import phonenumbers as pn
from datetime import datetime


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# we need to let Django handle the password hashing
from django.contrib.auth.hashers import make_password
from accounts.models import CustomUser, Profile

stallholders = pd.read_excel(
    '/usr/home/glenn/Documents/Rotary/Martinborough_Fair/Legacy_System/Extracts/extraStallholderData.xlsx')

# Open up a file to redirect print statements to for check outcomes
date = datetime.now(). strftime("%Y_%m_%d-%I:%M:%S_%p")
dir_name='//usr/home/glenn/Documents/Bin/Django/FairSystemProject/logs'
log_filename=f'userextract_{date}'
suffix = '.txt'

with open(os.path.join(dir_name, log_filename + suffix), 'w') as f:
    # let's create some users with default passwords equal to their username
    for i, row in stallholders.iterrows():
        tele_number = str(row['Tele'])
        phone2 = ''
        if not tele_number.find('/')==-1:
            trimmed_number = tele_number[:tele_number.index('/')]
            phone1 =  pn.format_number(pn.parse(trimmed_number, 'NZ'), pn.PhoneNumberFormat.NATIONAL)
            second_number = tele_number[tele_number.index('/')+1:]
            phone2= pn.format_number(pn.parse(second_number, 'NZ'), pn.PhoneNumberFormat.NATIONAL)
        else:
            phone1 = pn.format_number(pn.parse(tele_number, 'NZ'), pn.PhoneNumberFormat.NATIONAL)
        if CustomUser.objects.filter(reference_id=row['StallHolderID']).exists():
            print('Stallholder name {} with legacy ID {} already exists'.format(row['FNAME'], row['StallHolderID']), file=f)
        else:
            CustomUser.objects.create(
                reference_id=row['StallHolderID'],
                username=row['FNAME'].title()[0] + row['Surname'].title(),
                first_name=row['FNAME'].title(),
                last_name=row['Surname'].title(),
                email=row['EMAIL'],
                phone=phone1,
                password=make_password(row['FNAME'].title()),
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
