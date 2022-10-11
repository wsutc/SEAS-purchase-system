# Generated by Django 4.0.3 on 2022-10-11 17:11

from django.db import migrations

import web_project.fields


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0122_purchaserequest_new_st'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='purchaserequest',
            name='new_st',
        ),
        migrations.AlterField(
            model_name='purchaserequest',
            name='sales_tax_rate',
            field=web_project.fields.SimplePercentageField(decimal_places=4, max_digits=10, null=True, verbose_name='sales tax rate'),
        ),
    ]
