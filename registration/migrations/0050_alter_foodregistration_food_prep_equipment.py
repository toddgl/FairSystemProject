# Generated by Django 4.1.10 on 2023-08-14 18:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("registration", "0049_alter_foodregistration_food_prep_equipment"),
    ]

    operations = [
        migrations.AlterField(
            model_name="foodregistration",
            name="food_prep_equipment",
            field=models.ManyToManyField(
                blank=True,
                related_name="food_registration",
                through="registration.FoodPrepEquipReq",
                to="registration.foodprepequipment",
            ),
        ),
    ]
