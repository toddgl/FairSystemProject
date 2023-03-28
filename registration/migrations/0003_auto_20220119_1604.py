# Generated by Django 3.2.11 on 2022-01-19 16:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('fairs', '0040_zone_location'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('registration', '0002_foodsaletype_stallcategory'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='stallcategory',
            options={'verbose_name_plural': 'StallCategories'},
        ),
        migrations.CreateModel(
            name='StallRegistration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('booking_status', django_fsm.FSMField(choices=[(1, 'Created'), (2, 'Submitted'), (3, 'Invoiced'), (4, 'Manual Payment'), (5, 'Poli Payment'), (6, 'Stripe Payment'), (7, 'Payment Completed'), (8, 'Allocation Review'), (9, 'Allocation Pending'), (10, 'Allocation Approved'), (11, 'Allocation Rejected'), (12, 'Refund Review'), (13, 'Refund Donated'), (14, 'Refund Rejected'), (15, 'Refund Approved'), (16, 'Booked'), (17, 'Cancelled')], default=1, max_length=50, protected=True, verbose_name='Registration State')),
                ('stall_manager_name', models.CharField(max_length=150)),
                ('trestle_required', models.BooleanField(default=False)),
                ('trestle_quantity', models.IntegerField(default=0)),
                ('stall_shelter', models.TextField()),
                ('power_required', models.BooleanField(default=False)),
                ('total_charge', models.DecimalField(decimal_places=2, max_digits=8)),
                ('selling_food', models.BooleanField(default=False)),
                ('event_power', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='stall_registrations', to='fairs.eventpower', verbose_name='eventpower')),
                ('event_site', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='stall_registrations', to='fairs.eventsite', verbose_name='eventsite')),
                ('stall_category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='stall_registrations', to='registration.stallcategory')),
                ('stallholder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'StallRegistrations',
            },
        ),
    ]
