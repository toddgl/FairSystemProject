# Generated by Django 4.2.13 on 2024-06-10 21:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0056_stallregistration_is_invoiced'),
        ('payment', '0015_delete_discountitem'),
    ]

    operations = [
        migrations.CreateModel(
            name='DiscountItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('discount_amount', models.DecimalField(decimal_places=2, max_digits=8)),
                ('stall_registration', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='registration.stallregistration')),
            ],
        ),
    ]
