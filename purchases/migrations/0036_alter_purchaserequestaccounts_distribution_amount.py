# Generated by Django 4.0.3 on 2022-05-25 17:08

from django.db import migrations
import djmoney.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0035_purchaserequestaccounts_distribution_percent_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchaserequestaccounts',
            name='distribution_amount',
            field=djmoney.models.fields.MoneyField(blank=True, decimal_places=2, default_currency='USD', max_digits=14, null=True, verbose_name='Distribution'),
        ),
    ]
