# Generated by Django 4.0.3 on 2022-06-14 18:17

from decimal import Decimal

import djmoney.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("purchases", "0008_purchaseorder_tracker_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="manufacturer",
            name="mfg_logo",
            field=models.ImageField(
                blank=True,
                upload_to="manufacturers",
                verbose_name="Manufacturer Logo (optional)",
            ),
        ),
        migrations.AlterField(
            model_name="purchaseorder",
            name="shipping",
            field=djmoney.models.fields.MoneyField(
                decimal_places=2,
                default=Decimal("0"),
                default_currency="USD",
                max_digits=14,
                verbose_name="Shipping ($)",
            ),
        ),
    ]