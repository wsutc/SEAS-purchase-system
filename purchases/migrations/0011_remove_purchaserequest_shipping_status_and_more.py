# Generated by Django 4.0.3 on 2022-06-15 15:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("purchases", "0010_purchaserequest_carrier_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="purchaserequest",
            name="shipping_status",
        ),
        migrations.RemoveField(
            model_name="purchaserequest",
            name="shipping_status_datetime",
        ),
        migrations.RemoveField(
            model_name="purchaserequest",
            name="tracker_id",
        ),
        migrations.CreateModel(
            name="Tracker",
            fields=[
                (
                    "id",
                    models.CharField(
                        editable=False,
                        max_length=100,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("tracking_number", models.CharField(max_length=100)),
                ("events", models.JSONField(default=None, null=True)),
                (
                    "carrier",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="purchases.carrier",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="purchaserequest",
            name="tracker",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="purchases.tracker",
            ),
        ),
        migrations.AddIndex(
            model_name="tracker",
            index=models.Index(fields=["id"], name="purchases_t_id_fafc95_idx"),
        ),
    ]