# Generated by Django 4.1.5 on 2023-01-29 22:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("fairs", "0063_rename_allocation_email_fair_allocation_email_date"),
    ]

    operations = [
        migrations.RenameField(
            model_name="fair",
            old_name="is_active",
            new_name="is_activated",
        ),
    ]
