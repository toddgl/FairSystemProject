# Generated by Django 4.2.14 on 2025-02-18 20:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("payment", "0023_paymenthistory_amount_credited"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="discountitem",
            options={
                "verbose_name": "discountitem",
                "verbose_name_plural": "discountitems",
            },
        ),
        migrations.AlterModelOptions(
            name="invoiceitem",
            options={
                "verbose_name": "invoiceitem",
                "verbose_name_plural": "invoiceitems",
            },
        ),
    ]
