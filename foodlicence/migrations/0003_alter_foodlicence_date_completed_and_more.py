# Generated by Django 4.2.13 on 2024-07-04 22:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodlicence', '0002_alter_foodlicence_licence_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='foodlicence',
            name='date_completed',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='foodlicence',
            name='food_licence_batch',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='food_licence_batch', to='foodlicence.foodlicencebatch'),
        ),
    ]
