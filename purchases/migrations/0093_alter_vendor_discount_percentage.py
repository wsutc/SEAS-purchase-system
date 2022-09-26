# Generated by Django 4.0.3 on 2022-09-22 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0092_alter_vendor_discount_percentage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendor',
            name='discount_percentage',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=15),
        ),
    ]
