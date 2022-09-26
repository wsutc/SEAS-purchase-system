# Generated by Django 4.0.3 on 2022-09-06 15:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("purchases", "0067_tracker_active"),
    ]

    operations = [
        migrations.CreateModel(
            name="VendorOrder",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("slug", models.SlugField(editable=False, unique=True)),
                ("created_date", models.DateTimeField(auto_now_add=True)),
                ("name", models.CharField(max_length=50, verbose_name="order number")),
                ("link", models.URLField(verbose_name="link")),
                (
                    "purchase_requests",
                    models.ManyToManyField(
                        to="purchases.purchaserequest", verbose_name="purchase_requests"
                    ),
                ),
                (
                    "vendor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="purchases.vendor",
                    ),
                ),
            ],
            options={
                "verbose_name": "vendor order",
                "verbose_name_plural": "vendor orders",
            },
        ),
    ]