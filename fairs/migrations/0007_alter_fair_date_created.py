# Generated by Django 3.2.7 on 2021-10-12 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fairs', '0006_auto_20211012_1517'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fair',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]