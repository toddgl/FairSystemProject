# Generated by Django 4.2.14 on 2024-11-13 06:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("emails", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="email",
            name="stallholder",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="emails",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
