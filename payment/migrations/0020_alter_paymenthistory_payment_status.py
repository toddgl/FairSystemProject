# Generated by Django 4.2.14 on 2024-08-07 20:40

from django.db import migrations
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0019_paymenthistory_webhook_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymenthistory',
            name='payment_status',
            field=django_fsm.FSMField(choices=[('Pending', 'pending'), ('Superceded', 'superceded'), ('Cancelled', 'cancelled'), ('Completed', 'completed'), ('Failed', 'failed'), ('Reconciled', 'reconciled')], default='Pending', max_length=50, verbose_name='Payment State'),
        ),
    ]
