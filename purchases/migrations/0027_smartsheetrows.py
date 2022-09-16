# Generated by Django 4.0.3 on 2022-06-23 19:00

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("purchases", "0026_remove_purchaseorderaccounts_accounts_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="SmartsheetRows",
            fields=[
                (
                    "row_id",
                    models.CharField(
                        editable=False, max_length=50, primary_key=True, serialize=False
                    ),
                ),
                ("number", models.CharField(editable=False, max_length=30)),
                ("status", models.CharField(max_length=50)),
                (
                    "required_approver_approval",
                    models.CharField(max_length=50, null=True),
                ),
                (
                    "requestor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="purchases.requisitioner",
                    ),
                ),
                (
                    "required_approver",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
