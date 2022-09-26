# Generated by Django 4.0.3 on 2022-06-16 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0012_tracker_shipment_id_tracker_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='requisitioner',
            name='wsu_id',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='tracker',
            name='events',
            field=models.JSONField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='tracker',
            name='shipment_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]