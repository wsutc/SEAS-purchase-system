import csv, os
from logging import exception
import MySQLdb

from django.core.management.base import BaseCommand

from purchases.models.models_metadata import Accounts
from django.conf import settings


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("csv_file", nargs="+", type=str)

    def handle(self, *args, **kwargs):
        row_count = 0
        added_rows = 0
        skipped_rows = 0
        path = os.path.join(settings.BASE_DIR, kwargs["csv_file"][0])
        self.stdout.write(self.style.NOTICE("Path: %s" % path))
        with open(path, encoding="utf8") as f:
            reader = csv.reader(f)
            for row in reader:
                try:
                    row_count += 1
                    if row[5]:
                        object, created = Accounts.objects.update_or_create(
                            program_workday=row[5],
                            defaults={
                                "budget_code": row[1],
                                "fund": row[4],
                                "account_title": row[2],
                                "account": row[0],
                                "gift": row[6],
                                "grant": row[7],
                                "cost_center": row[8],
                            },
                        )
                    elif row[6]:
                        object, created = Accounts.objects.update_or_create(
                            gift=row[6],
                            defaults={
                                "budget_code": row[1],
                                "fund": row[4],
                                "account_title": row[2],
                                "account": row[0],
                                "program_workday": row[5],
                                "grant": row[7],
                                "cost_center": row[8],
                            },
                        )
                    elif row[7]:
                        object, created = Accounts.objects.update_or_create(
                            grant=row[7],
                            defaults={
                                "budget_code": row[1],
                                "fund": row[4],
                                "account_title": row[2],
                                "account": row[0],
                                "gift": row[6],
                                "program_workday": row[6],
                                "cost_center": row[8],
                            },
                        )
                    else:
                        self.stdout.write(
                            self.style.ERROR('No match for "%s"' % row[2])
                        )
                        continue
                    if created:
                        self.stdout.write(
                            self.style.NOTICE('Created "%s".' % object.account_title)
                        )
                        added_rows += 1
                    else:
                        self.stdout.write(
                            self.style.NOTICE('Updated "%s".' % object.account_title)
                        )
                except:
                    self.stdout.write(
                        self.style.ERROR(
                            'Unable to create/update object "%s".' % row[0]
                        )
                    )
                    skipped_rows += 1

            self.stdout.write(self.style.SUCCESS("Total Rows: %s" % row_count))
            self.stdout.write(self.style.SUCCESS("Added Rows: %s" % added_rows))
            self.stdout.write(self.style.SUCCESS("Skipped Rows: %s" % skipped_rows))
