# Generated by Django 4.0.3 on 2022-05-20 16:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0023_spendcategory_remove_purchaserequest_accounts_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaserequest',
            name='accounts',
            field=models.ManyToManyField(through='purchases.PurchaseRequestAccounts', to='purchases.accounts'),
        ),
    ]
