# Generated by Django 3.2.12 on 2022-03-23 20:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0012_auto_20220321_2143'),
    ]

    operations = [
        migrations.AddField(
            model_name='foodregistration',
            name='has_food_prep',
            field=models.BooleanField(default=False),
        ),
    ]
