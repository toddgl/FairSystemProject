# Generated by Django 3.2.11 on 2022-01-21 17:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('registration', '0003_auto_20220119_1604'),
    ]

    operations = [
        migrations.CreateModel(
            name='FoodPrepEquipReq',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('electrical_powered', models.BooleanField(default=False)),
                ('gas_powered', models.BooleanField(default=False)),
                ('food_prep_equipment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='food_prep_equip', to='registration.foodprepequipment', verbose_name='FoodPrepEquipment')),
            ],
        ),
        migrations.CreateModel(
            name='RegistrationComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField()),
                ('convener_only_comment', models.BooleanField(default=False)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='registration_comment_created_by', to=settings.AUTH_USER_MODEL)),
                ('stall_registration', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registration_comments', to='registration.stallregistration', verbose_name='stallregistration')),
            ],
        ),
        migrations.CreateModel(
            name='FoodRegistration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('food_display_method', models.TextField()),
                ('has_food_certificate', models.BooleanField(default=False)),
                ('food_registration_certificate', models.FileField(upload_to='media/food_certificates')),
                ('certificate_expiry_date', models.DateField()),
                ('food_fair_consumed', models.BooleanField(default=False)),
                ('food_source', models.TextField()),
                ('has_food_storage_prep', models.BooleanField(default=False)),
                ('food_storage_prep_method', models.TextField()),
                ('hygiene_methods', models.TextField()),
                ('food_prep_equipment', models.ManyToManyField(related_name='food_registration', through='registration.FoodPrepEquipReq', to='registration.FoodPrepEquipment')),
                ('food_stall_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='food_registration', to='registration.foodsaletype')),
                ('registration', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='food_registration', to='registration.stallregistration')),
            ],
            options={
                'verbose_name_plural': 'FoodRegistrations',
            },
        ),
        migrations.AddField(
            model_name='foodprepequipreq',
            name='food_registration',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='food_prep_equip_req', to='registration.foodregistration', verbose_name='FoodPrepEquipmentRequired'),
        ),
    ]
