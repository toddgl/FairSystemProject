# Generated by Django 3.2.7 on 2021-09-27 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fairs', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='fair',
            name='activation_date',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='fair',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
    ]
