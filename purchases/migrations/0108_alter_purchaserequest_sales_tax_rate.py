# Generated by Django 4.0.3 on 2022-09-30 15:32

from django.db import migrations

import web_project.fields


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0107_remove_purchaserequest_sales_tax_perc_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchaserequest',
            name='sales_tax_rate',
            field=web_project.fields.PercentageField(field_decimal_places=6, max_digits=10),
        ),
    ]
