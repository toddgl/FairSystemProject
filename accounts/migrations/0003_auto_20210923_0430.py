# Generated by Django 3.2.7 on 2021-09-23 04:30

import django.core.validators
from django.db import migrations, models
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20210917_0952'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customuser',
            options={'verbose_name': 'customuser', 'verbose_name_plural': 'customusers'},
        ),
        migrations.AddField(
            model_name='customuser',
            name='created_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='customuser',
            name='modified_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='customuser',
            name='phone',
            field=models.CharField(default='(027)1234567', max_length=13, unique=True, validators=[django.core.validators.RegexValidator(regex='/^(\\((03|04|06|07|09)\\)\\d{7})|(\\((021|022|025|027|028|029)\\)\\d{6,8})|((0508|0800|0900)\\d{5,8})$/')]),
        ),
        migrations.AddField(
            model_name='customuser',
            name='role',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'admin'), (2, 'convener'), (3, 'stallholder'), (4, 'regulator')], default=3, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='uid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='Public identifier'),
        ),
    ]