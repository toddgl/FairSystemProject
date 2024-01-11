# Generated by Django 4.2.8 on 2024-01-09 20:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("registration", "0051_stallregistration_is_cancelled"),
    ]

    operations = [
        migrations.AlterField(
            model_name="foodregistration",
            name="food_registration_certificate",
            field=models.FileField(
                blank=True, null=True, upload_to="food_certificates/2024"
            ),
        ),
        migrations.AlterField(
            model_name="stallregistration",
            name="vehicle_image",
            field=models.ImageField(blank=True, null=True, upload_to="vehicles/2024"),
        ),
    ]
