# Generated by Django 4.0.3 on 2022-05-19 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0014_product_last_price_currency_alter_product_last_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='manufacturer',
            name='slug',
            field=models.SlugField(default='', editable=False, max_length=255),
        ),
    ]
