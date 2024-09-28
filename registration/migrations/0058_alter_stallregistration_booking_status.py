# Generated by Django 4.2.16 on 2024-09-16 08:55

from django.db import migrations
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0057_alter_stallregistration_booking_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stallregistration',
            name='booking_status',
            field=django_fsm.FSMField(choices=[('Created', 'Created'), ('Submitted', 'Submitted'), ('Invoiced', 'Invoiced'), ('Amended', 'Amended'), ('Payment Completed', 'Payment Completed'), ('Allocation Review', 'Allocation Review'), ('Allocation Pending', 'Allocation Pending'), ('Allocation Approved', 'Allocation Approved'), ('Allocation Cancelled', 'Allocation Rejected'), ('Refund Review', 'Refund Review'), ('Refund Donated', 'Refund Donated'), ('Refund Rejected', 'Refund Rejected'), ('Refund Approved', 'Refund Approved'), ('Booked', 'Booked'), ('Cancelled', 'Cancelled')], default='Created', max_length=50, verbose_name='Registration State'),
        ),
    ]