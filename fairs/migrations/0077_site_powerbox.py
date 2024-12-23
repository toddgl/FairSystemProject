# Generated by Django 4.2.14 on 2024-11-28 10:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("fairs", "0076_site_has_power"),
    ]

    operations = [
        migrations.AddField(
            model_name="site",
            name="powerbox",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="site_powerbox",
                to="fairs.powerbox",
                verbose_name="powerbox",
            ),
        ),
    ]
