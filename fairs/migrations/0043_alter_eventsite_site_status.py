# Generated by Django 3.2.11 on 2022-02-21 21:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fairs', '0042_auto_20220126_2047'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventsite',
            name='site_status',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Available to be booked'), (2, 'Allocated to a stallholder'), (3, 'Pending finalisation of the booking'), (4, 'Booked'), (5, 'Not available for this event'), (6, 'No longer used - was from a previous fair')], default=1),
        ),
    ]
