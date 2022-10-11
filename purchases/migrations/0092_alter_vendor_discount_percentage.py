# Generated by Django 4.0.3 on 2022-09-22 16:55

from django.db import migrations

import web_project.fields


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0091_alter_vendor_discount_percentage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendor',
            name='discount_percentage',
            field=web_project.fields.SimplePercentageField(decimal_places=4, default=0, max_digits=15),
        ),
    ]
