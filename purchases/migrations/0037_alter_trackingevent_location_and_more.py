# Generated by Django 4.0.3 on 2022-07-27 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0036_remove_purchaserequest_carrier_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trackingevent',
            name='location',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='trackingevent',
            name='stage',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
