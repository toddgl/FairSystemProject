# Generated by Django 3.2.8 on 2021-10-17 21:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fairs', '0014_zone'),
    ]

    operations = [
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('site_name', models.CharField(max_length=40)),
                ('site_size', models.CharField(max_length=5)),
                ('zone', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='fairs.zone')),
            ],
            options={
                'verbose_name_plural': 'Sites',
            },
        ),
    ]
