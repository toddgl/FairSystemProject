# Generated by Django 3.2.11 on 2022-01-26 16:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fairs', '0040_zone_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='event_sequence',
            field=models.PositiveSmallIntegerField(choices=[(1, 'First Event'), (2, 'Second Event')], default=1),
        ),
    ]
