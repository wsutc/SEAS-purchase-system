# Generated by Django 4.0.3 on 2022-05-26 17:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0004_item_manufacture_date_item_purchase_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='room',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.room'),
        ),
    ]
