# Generated by Django 4.2.10 on 2024-02-18 21:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fairs', '0068_alter_inventoryitem_item_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventoryitemfair',
            name='inventory_item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inventory_itemr', to='fairs.inventoryitem', verbose_name='inventory_items'),
        ),
    ]