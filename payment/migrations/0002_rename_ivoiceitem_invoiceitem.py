# Generated by Django 4.2.8 on 2023-12-31 21:46

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("fairs", "0066_alter_siteallocation_stall_registration"),
        ("payment", "0001_initial"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="IvoiceItem",
            new_name="InvoiceItem",
        ),
    ]