# Generated by Django 4.2.8 on 2024-01-09 20:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("fairs", "0066_alter_siteallocation_stall_registration"),
    ]

    operations = [
        migrations.AlterField(
            model_name="zonemap",
            name="map_pdf",
            field=models.FileField(upload_to="maps/2024"),
        ),
        migrations.AlterField(
            model_name="zonemap",
            name="year",
            field=models.CharField(default="2024", max_length=4),
        ),
    ]
