# Generated by Django 3.2.13 on 2022-07-05 17:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('fairs', '0046_auto_20220609_2024'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Year', models.CharField(default='2022', max_length=4)),
                ('is_skipped', models.BooleanField(default=False)),
                ('number_events', models.IntegerField()),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='site_history', to='fairs.site', verbose_name='site')),
                ('stallholder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='site_history', to=settings.AUTH_USER_MODEL, verbose_name='custom_user')),
            ],
        ),
    ]
