# Generated by Django 4.0.3 on 2022-09-22 16:23

from django.db import migrations

import web_project.fields


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0090_simpleproduct_rank'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendor',
            name='discount_percentage',
            field=web_project.fields.PercentageField(decimal_places=0, default=0, max_digits=15),
        ),
    ]
