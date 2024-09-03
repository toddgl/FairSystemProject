import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import Group
from accounts.models import CustomUser  # Adjust import based on your app name

try:
    stallholder_group = Group.objects.get(name='stallholder')
    users_to_update = CustomUser.objects.filter(role=3)

    for user in users_to_update:
        user.groups.add(stallholder_group)
        user.save()

    print(f'Successfully added {users_to_update.count()} users to the stallholder group.')
except Group.DoesNotExist:
    print('Stallholder group does not exist.')
