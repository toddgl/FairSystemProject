# Generated by Django 4.1.9 on 2023-06-20 09:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("registration", "0036_alter_foodprepequipreq_how_powered"),
    ]

    operations = [
        migrations.AlterField(
            model_name="foodregistration",
            name="food_registration_certificate",
            field=models.FileField(blank=True, upload_to="media/food_certificates"),
        ),
    ]
