# Generated by Django 4.0.3 on 2022-09-29 22:20

from django.db import migrations

import web_project.fields


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0105_rename_accounts_external_purchaserequest_accounts_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaserequest',
            name='sales_tax_perc',
            field=web_project.fields.SimplePercentageField(blank=True, decimal_places=6, default=0, max_digits=10),
        ),
    ]
