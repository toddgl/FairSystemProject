# Generated by Django 4.1.9 on 2023-06-22 16:26

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("registration", "0037_alter_foodregistration_food_registration_certificate"),
    ]

    operations = [
        migrations.AlterField(
            model_name="foodregistration",
            name="food_source",
            field=models.TextField(default=False),
        ),
        migrations.AlterField(
            model_name="foodregistration",
            name="food_storage_prep_method",
            field=models.TextField(default=False),
        ),
    ]
