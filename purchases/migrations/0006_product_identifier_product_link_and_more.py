# Generated by Django 4.0.3 on 2022-03-30 20:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0005_alter_manufacturer_created_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='identifier',
            field=models.CharField(blank=True, max_length=50, verbose_name='Unique Identifier (ASIN/UPC/PN/etc.)'),
        ),
        migrations.AddField(
            model_name='product',
            name='link',
            field=models.URLField(blank=True, verbose_name='Direct Link'),
        ),
        migrations.AlterField(
            model_name='product',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Date Product Created'),
        ),
        migrations.AlterField(
            model_name='purchaseorder',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Created Date'),
        ),
        migrations.AlterField(
            model_name='purchaserequest',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Created Date'),
        ),
    ]
