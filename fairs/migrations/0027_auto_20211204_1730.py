# Generated by Django 3.2.9 on 2021-12-04 17:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fairs', '0026_rename_status_eventsite_site_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='site',
            name='site_size',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='site_sizes', to='fairs.inventoryitem'),
        ),
        migrations.AlterField(
            model_name='site',
            name='zone',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='zones', to='fairs.zone'),
        ),
    ]