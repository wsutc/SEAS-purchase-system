# Generated by Django 4.0.3 on 2022-09-30 15:31

from django.db import migrations

import web_project.fields


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0106_purchaserequest_sales_tax_perc'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='purchaserequest',
            name='sales_tax_perc',
        ),
        migrations.AlterField(
            model_name='purchaserequest',
            name='sales_tax_rate',
            field=web_project.fields.PercentageField(field_decimal_places=9, max_digits=10),
        ),
    ]
