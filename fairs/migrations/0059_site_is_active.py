# Generated by Django 4.1.5 on 2023-01-13 21:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fairs", "0058_alter_event_event_name_alter_fair_fair_name_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="site",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
    ]
