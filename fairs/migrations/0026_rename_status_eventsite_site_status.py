# Generated by Django 3.2.8 on 2021-11-14 08:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fairs', '0025_alter_eventsite_status'),
    ]

    operations = [
        migrations.RenameField(
            model_name='eventsite',
            old_name='status',
            new_name='site_status',
        ),
    ]
