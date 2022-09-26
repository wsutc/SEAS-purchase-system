# Generated by Django 4.0.3 on 2022-06-22 16:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("purchases", "0023_alter_ledgers_purchase_request"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ledgers",
            name="account",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="purchases.balances"
            ),
        ),
        migrations.AlterField(
            model_name="ledgers",
            name="purchase_request",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                to="purchases.purchaserequest",
            ),
        ),
    ]