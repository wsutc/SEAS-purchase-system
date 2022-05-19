# Generated by Django 4.0.3 on 2022-05-18 17:04

from django.db import migrations, models
import purchases.models


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0010_alter_vendor_state'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendor',
            name='state',
            field=models.ForeignKey(blank=True, null=True, on_delete=purchases.models.State, to='purchases.state'),
        ),
    ]
