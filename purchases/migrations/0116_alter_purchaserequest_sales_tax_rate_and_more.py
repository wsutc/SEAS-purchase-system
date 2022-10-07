# Generated by Django 4.0.3 on 2022-10-07 23:30

from django.db import migrations

import web_project.fields


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0115_remove_purchaserequest_new_tax_rate_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchaserequest',
            name='sales_tax_rate',
            field=web_project.fields.PercentageField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='vendor',
            name='discount_percentage',
            field=web_project.fields.PercentageField(decimal_places=2, max_digits=15),
        ),
    ]