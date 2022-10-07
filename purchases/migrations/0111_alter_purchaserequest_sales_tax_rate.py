# Generated by Django 4.0.3 on 2022-10-07 16:41

from django.db import migrations

import web_project.fields


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0110_simpleproduct_taxable_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchaserequest',
            name='sales_tax_rate',
            field=web_project.fields.PercentageField(field_decimal_places=6, max_digits=10),
        ),
    ]
