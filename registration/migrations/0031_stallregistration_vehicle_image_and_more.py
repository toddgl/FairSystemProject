# Generated by Django 4.1.4 on 2023-01-11 14:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("registration", "0030_auto_20221203_0844"),
    ]

    operations = [
        migrations.AddField(
            model_name="stallregistration",
            name="vehicle_image",
            field=models.ImageField(null=True, upload_to="vehicles/2023"),
        ),
        migrations.AddField(
            model_name="stallregistration",
            name="vehicle_length",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="stallregistration",
            name="vehicle_on_site",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="stallregistration",
            name="vehicle_width",
            field=models.FloatField(blank=True, null=True),
        ),
    ]
