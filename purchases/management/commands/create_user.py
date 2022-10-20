"""Doesn't currently do anything!"""
# import os
import sys

# from django.apps import apps
from django.conf import settings

# from django.core.exceptions import FieldDoesNotExist
from django.core.management import execute_from_command_line
from django.core.management.base import BaseCommand
from django.db import migrations, models

# from django.db.migrations import AlterField
# from django.db.models import signals

# import manage


class Command(BaseCommand):
    help = "Creates super user from underneath Requisitioner"

    def handle(self, *create_su_args, **options):
        # run `migrate` command
        migrate_args = sys.argv.copy()
        migrate_args[1] = "migrate"
        migrate_args[2] = "purchases"
        migrate_args[3] = "0064"
        execute_from_command_line(migrate_args)

        # run `createsuperuser` command
        create_su_args = sys.argv.copy()
        create_su_args[1] = "createsuperuser"
        execute_from_command_line(create_su_args)

        migrations.AddField(
            model_name="requisitioner",
            name="user",
            field=models.OneToOneField(
                on_delete=models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        )
