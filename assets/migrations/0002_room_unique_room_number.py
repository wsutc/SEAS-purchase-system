# Generated by Django 4.2.2 on 2023-07-13 20:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("assets", "0001_initial"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="room",
            constraint=models.UniqueConstraint(
                fields=("building", "number"), name="unique_room_number"
            ),
        ),
    ]