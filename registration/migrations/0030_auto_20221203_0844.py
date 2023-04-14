# Generated by Django 3.2.16 on 2022-12-03 08:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fairs', '0055_eventsite_notes'),
        ('registration', '0029_alter_registrationcomment_comment_parent'),
    ]

    operations = [
        migrations.AddField(
            model_name='registrationcomment',
            name='fair',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='fairs.fair'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='registrationcomment',
            name='is_done',
            field=models.BooleanField(default=False),
        ),
    ]