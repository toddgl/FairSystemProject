# Generated by Django 4.1.9 on 2023-07-06 21:22

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("registration", "0039_foodregistration_is_valid"),
    ]

    operations = [
        migrations.AlterField(
            model_name="foodregistration",
            name="food_source",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="foodregistration",
            name="food_storage_prep_method",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="foodregistration",
            name="has_food_prep",
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="foodregistration",
            name="is_valid",
            field=models.BooleanField(blank=True, null=True),
        ),
    ]