# Generated by Django 3.2.10 on 2021-12-20 17:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fairs', '0035_inventoryitem_item_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inventoryitem',
            name='is_power_connection',
        ),
    ]
