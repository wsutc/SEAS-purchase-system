# Generated by Django 4.0.3 on 2022-10-10 21:44

from django.db import migrations, models
from django.utils.translation import gettext_lazy as _


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0118_remove_purchaserequest_sales_tax_rate_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name="purchaserequest",
            name="new_st",
            field=models.CharField(_("test"), max_length=50),
        ),
        migrations.AddField(
            model_name="purchaserequest",
            name="sales_tax_rate",
            field=models.CharField(_("test"), max_length=50),
        ),
        migrations.RemoveField(
            model_name='purchaserequest',
            name='new_st',
        ),
        migrations.RemoveField(
            model_name='purchaserequest',
            name='sales_tax_rate',
        ),
    ]
