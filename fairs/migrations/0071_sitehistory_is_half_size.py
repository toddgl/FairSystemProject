# Generated by Django 4.2.13 on 2024-06-09 21:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fairs', '0070_inventoryitemfair_is_percentage_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitehistory',
            name='is_half_size',
            field=models.BooleanField(default=False),
        ),
    ]
