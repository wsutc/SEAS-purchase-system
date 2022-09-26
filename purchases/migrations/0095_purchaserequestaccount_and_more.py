# Generated by Django 4.0.3 on 2022-09-26 17:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_basetransaction_amount_and_more'),
        ('purchases', '0094_alter_vendor_discount_percentage'),
    ]

    operations = [
        migrations.CreateModel(
            name='PurchaseRequestAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('distribution_type', models.CharField(choices=[('P', 'Percent'), ('A', 'Amount')], default='P', max_length=1)),
                ('distribution_input', models.FloatField(default=100)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='accounts.account')),
            ],
            options={
                'verbose_name_plural': 'purchase request accounts',
            },
        ),
        migrations.AddField(
            model_name='purchaserequest',
            name='accounts_external',
            field=models.ManyToManyField(through='purchases.PurchaseRequestAccount', to='accounts.account'),
        ),
        migrations.AddField(
            model_name='purchaserequestaccount',
            name='purchase_request',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='purchases.purchaserequest'),
        ),
        migrations.AddField(
            model_name='purchaserequestaccount',
            name='spend_category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='purchases.spendcategory'),
        ),
    ]
