# Generated by Django 4.0.3 on 2022-09-29 20:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_spendcategory'),
        ('purchases', '0104_remove_purchaserequestaccount_spend_category'),
    ]

    operations = [
        migrations.RenameField(
            model_name='purchaserequest',
            old_name='accounts_external',
            new_name='accounts',
        ),
        migrations.AlterField(
            model_name='purchaserequestaccount',
            name='account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='accounts.account', verbose_name='account'),
        ),
        migrations.AlterField(
            model_name='purchaserequestaccount',
            name='spend_category_ext',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='accounts.spendcategory', verbose_name='spend category'),
        ),
        migrations.DeleteModel(
            name='PurchaseRequestAccounts',
        ),
    ]
