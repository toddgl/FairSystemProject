# Generated by Django 3.2.10 on 2021-12-27 16:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fairs', '0039_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='zone',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='zone_location', to='fairs.location'),
        ),
    ]
