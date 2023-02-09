# Generated by Django 4.0.9 on 2023-02-09 05:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_spendcategory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='account',
            field=models.CharField(help_text='in form XXXX-XXXX.', max_length=10, null=True, verbose_name='account'),
        ),
        migrations.AlterField(
            model_name='account',
            name='budget_code',
            field=models.CharField(help_text='usually first four characters of account', max_length=5, null=True, verbose_name='budget code'),
        ),
    ]