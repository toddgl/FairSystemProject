# Generated by Django 3.2.8 on 2021-10-18 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fairs', '0016_eventsite'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='sites',
            field=models.ManyToManyField(related_name='events', through='fairs.EventSite', to='fairs.Site'),
        ),
    ]
