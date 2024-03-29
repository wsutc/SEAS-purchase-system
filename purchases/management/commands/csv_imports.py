import csv

# import os
from pathlib import Path

# import MySQLdb
from django.conf import settings
from django.core.management.base import BaseCommand

from purchases.models import Carrier

# from logging import exception


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("csv_file", nargs="+", type=str)

    def handle(self, *args, **kwargs):
        row_count = 0
        added_rows = 0
        skipped_rows = 0
        path = Path(settings.BASE_DIR, kwargs["csv_file"][0])
        self.stdout.write(self.style.NOTICE("Path: %s" % path))
        with Path.open(path, encoding="utf8") as f:
            reader = csv.reader(f)
            for row in reader:
                try:
                    carrier, created = Carrier.objects.update_or_create(
                        name=row[1],
                        defaults={"website": row[4], "carrier_code": row[0]},
                    )
                    row_count += 1
                    if created:
                        self.stdout.write(
                            self.style.NOTICE('Created "%s".' % carrier.name),
                        )
                        added_rows += 1
                    else:
                        self.stdout.write(
                            self.style.NOTICE('"%s" updated.' % carrier.name),
                        )
                except Exception:
                    self.stdout.write(
                        self.style.ERROR("Unable to create/update carrier %s" % row[1]),
                    )
                    skipped_rows += 1

            self.stdout.write(self.style.SUCCESS("Total Rows: %s" % row_count))
            self.stdout.write(self.style.SUCCESS("Added Rows: %s" % added_rows))
            self.stdout.write(self.style.SUCCESS("Skipped Rows: %s" % added_rows))
