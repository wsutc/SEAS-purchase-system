# Generated by Django 4.0.10 on 2023-04-24 17:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_alter_account_account_alter_account_budget_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='account',
            field=models.CharField(blank=True, help_text='in form XXXX-XXXX.', max_length=10, null=True, verbose_name='account'),
        ),
        migrations.AlterField(
            model_name='account',
            name='budget_code',
            field=models.CharField(blank=True, help_text='usually first four characters of account', max_length=5, null=True, verbose_name='budget code'),
        ),
    ]