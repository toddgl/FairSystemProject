# Generated by Django 3.2.9 on 2021-12-15 15:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fairs', '0032_alter_inventoryitem_site_size'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventoryitem',
            name='site_size',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
    ]