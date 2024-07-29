# accounts/management/commands/set_stallholder_group.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from accounts.models import CustomUser


class Command(BaseCommand):
    """
    This will execute the command and add all users with the "stallholder" role to the "stallholder" group, providing feedback on the console for each user updated.
    Usage: python3 manage.py set_stallholder_group
    """
    help = 'Assign all users with role stallholder to the stallholder group'

    def handle(self, *args, **kwargs):
        try:
            stallholder_group = Group.objects.get(name='stallholder')
        except Group.DoesNotExist:
            self.stdout.write(self.style.ERROR('Stallholder group does not exist'))
            return

        stallholders = CustomUser.objects.filter(role=CustomUser.STALLHOLDER)

        for user in stallholders:
            user.groups.add(stallholder_group)
            self.stdout.write(self.style.SUCCESS(f'Added {user.username} to stallholder group'))

        self.stdout.write(self.style.SUCCESS('Successfully updated all stallholders'))
