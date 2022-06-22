# Generated by Django 4.0.3 on 2022-06-22 16:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0024_alter_ledgers_account_alter_ledgers_purchase_request'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Balances',
            new_name='Balance',
        ),
        migrations.RenameModel(
            old_name='Ledgers',
            new_name='Transaction',
        ),
        migrations.AlterModelOptions(
            name='balance',
            options={},
        ),
        migrations.AlterModelOptions(
            name='transaction',
            options={'ordering': ['-processed_datetime']},
        ),
        migrations.RenameField(
            model_name='transaction',
            old_name='account',
            new_name='balance',
        ),
    ]
