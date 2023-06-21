# Generated by Django 4.1.8 on 2023-05-04 20:39

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("registration", "0034_registrationcomment_is_archived"),
    ]

    operations = [
        migrations.AddField(
            model_name="foodprepequipreq",
            name="equipment_quantity",
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name="foodprepequipreq",
            name="how_powered",
            field=models.CharField(
                choices=[(1, "Electric Powered"), (2, "Gas Powered")],
                default=1,
                max_length=11,
            ),
        ),
    ]