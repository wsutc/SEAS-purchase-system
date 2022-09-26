# Generated by Django 4.0.3 on 2022-08-25 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0064_add_vendor_created_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentnumber',
            name='last_generated_date',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='vendor',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]