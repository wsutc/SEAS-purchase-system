# Generated by Django 4.0.3 on 2022-06-22 17:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0025_rename_balances_balance_rename_ledgers_transaction_and_more'),
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='purchase_order',
        ),
        migrations.AddField(
            model_name='item',
            name='purchase_request',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='purchases.purchaserequest'),
        ),
    ]
