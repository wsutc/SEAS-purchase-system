# Generated by Django 4.2.2 on 2023-07-27 22:07

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("purchases", "0074_alter_balance_balance_currency_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="vendor",
            name="product_link",
            field=models.URLField(
                blank=True,
                help_text="use {number} as the placeholder for the identifier",
                verbose_name="format string for direct product links",
            ),
        ),
    ]
