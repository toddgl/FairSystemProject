# Generated by Django 4.2.14 on 2024-10-11 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0016_alter_customuser_reference_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="address1",
            field=models.CharField(blank=True, max_length=70),
        ),
        migrations.AlterField(
            model_name="profile",
            name="org_name",
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
