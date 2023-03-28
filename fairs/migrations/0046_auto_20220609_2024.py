# Generated by Django 3.2.13 on 2022-06-09 20:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fairs', '0045_zonemap'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='zone',
            name='map_pdf',
        ),
        migrations.AlterField(
            model_name='zonemap',
            name='map_pdf',
            field=models.FileField(upload_to='maps/2022'),
        ),
        migrations.AlterField(
            model_name='zonemap',
            name='year',
            field=models.CharField(default='2022', max_length=4),
        ),
        migrations.AlterField(
            model_name='zonemap',
            name='zone',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='zone_map', to='fairs.zone', verbose_name='zone'),
        ),
    ]
