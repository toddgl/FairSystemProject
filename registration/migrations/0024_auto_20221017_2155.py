# Generated by Django 3.2.16 on 2022-10-17 21:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fairs', '0054_alter_siteallocation_stall_registration'),
        ('registration', '0023_alter_foodprepequipreq_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='foodregistration',
            options={'verbose_name': 'foodregistration', 'verbose_name_plural': 'foodregistrations'},
        ),
        migrations.AddField(
            model_name='stallcategory',
            name='has_inventory_item',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='stallcategory',
            name='inventory_item',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='inventory_item', to='fairs.inventoryitem'),
        ),
    ]
