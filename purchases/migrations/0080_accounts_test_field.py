# Generated by Django 4.0.3 on 2022-09-12 17:32

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("purchases", "0079_remove_accounts_slug"),
    ]

    operations = [
        migrations.AddField(
            model_name="accounts",
            name="created_date",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
    ]