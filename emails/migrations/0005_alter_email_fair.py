# Generated by Django 4.2.14 on 2024-11-16 22:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("fairs", "0076_site_has_power"),
        ("emails", "0004_alter_email_managers_email_fair"),
    ]

    operations = [
        migrations.AlterField(
            model_name="email",
            name="fair",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="emails_fair",
                to="fairs.fair",
                verbose_name="fair",
            ),
        ),
    ]
