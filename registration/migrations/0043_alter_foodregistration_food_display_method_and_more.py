# Generated by Django 4.1.10 on 2023-07-18 09:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("registration", "0042_foodregistration_cert_filetype"),
    ]

    operations = [
        migrations.AlterField(
            model_name="foodregistration",
            name="food_display_method",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="foodregistration",
            name="food_prep_equipment",
            field=models.ManyToManyField(
                blank=True,
                null=True,
                related_name="food_registration",
                through="registration.FoodPrepEquipReq",
                to="registration.foodprepequipment",
            ),
        ),
        migrations.AlterField(
            model_name="foodregistration",
            name="food_storage_prep",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="foodregistration",
            name="hygiene_methods",
            field=models.TextField(blank=True, null=True),
        ),
    ]
