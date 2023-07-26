# Generated by Django 4.1.10 on 2023-07-24 08:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("fairs", "0066_alter_siteallocation_stall_registration"),
        ("registration", "0046_alter_foodregistration_cert_filetype_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="stallregistration",
            name="multi_site",
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name="AdditionalSiteRequirement",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "location_choice",
                    models.CharField(
                        choices=[("1", "Joined"), ("2", "Separate")],
                        default="1",
                        max_length=11,
                    ),
                ),
                ("site_quantity", models.IntegerField(default=1)),
                (
                    "site_size",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="Additional_site_size_requirement",
                        to="fairs.inventoryitem",
                    ),
                ),
                (
                    "stall_registration",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="additional_sites_required",
                        to="registration.stallregistration",
                        verbose_name="AdditionalSitesRequired",
                    ),
                ),
            ],
            options={
                "verbose_name": "addiitionalsiterequired",
                "verbose_name_plural": "addiitionalsiterequirements",
            },
        ),
    ]