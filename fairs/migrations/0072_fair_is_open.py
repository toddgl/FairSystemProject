# Generated by Django 4.2.14 on 2024-07-19 12:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fairs', '0071_sitehistory_is_half_size'),
    ]

    operations = [
        migrations.AddField(
            model_name='fair',
            name='is_open',
            field=models.BooleanField(default=False),
        ),
    ]
