# Generated by Django 3.2.8 on 2021-11-13 15:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fairs', '0023_alter_inventoryitem_options'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='eventsite',
            unique_together={('event', 'site')},
        ),
    ]
