# Generated by Django 3.2.14 on 2022-07-16 21:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0014_auto_20220716_2146'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='org_name',
            field=models.CharField(blank=True, default='', max_length=50),
            preserve_default=False,
        ),
    ]
