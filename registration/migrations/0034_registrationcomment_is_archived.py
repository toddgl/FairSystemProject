# Generated by Django 4.1.6 on 2023-02-20 22:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("registration", "0033_alter_stallregistration_vehicle_image_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="registrationcomment",
            name="is_archived",
            field=models.BooleanField(default=False),
        ),
    ]
