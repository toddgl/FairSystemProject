# Generated by Django 4.2.14 on 2025-03-03 20:08

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("registration", "0061_alter_foodprepequipment_power_load_amps"),
    ]

    operations = [
        migrations.AddField(
            model_name="stallregistration",
            name="date_created",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
    ]
