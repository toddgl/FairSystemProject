# Generated by Django 3.2.15 on 2022-10-10 20:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0019_alter_stallregistration_booking_status'),
        ('fairs', '0053_alter_event_event_sequence'),
    ]

    operations = [
        migrations.AlterField(
            model_name='siteallocation',
            name='stall_registration',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='site_allocation', to='registration.stallregistration', verbose_name='stall_registration'),
        ),
    ]
