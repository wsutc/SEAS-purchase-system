import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from purchases.models.models_metadata import SpendCategory


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
                    object, created = SpendCategory.objects.update_or_create(
                        object=row[1],
                        subobject=row[2],
                        defaults={
                            "code": row[4],
                            "description": row[5].split(" ", 1)[1],
                        },
                    )
                    row_count += 1
                    if created:
                        self.stdout.write(
                            self.style.NOTICE('Created "%s".' % object.description)
                        )
                        added_rows += 1
                    else:
                        self.stdout.write(
                            self.style.NOTICE('Updated "%s".' % object.name)
                        )
                except Exception:
                    self.stdout.write(
                        self.style.ERROR(
                            'Unable to create/update object "%s".' % row[1]
                        )
                    )
                    skipped_rows += 1

            self.stdout.write(self.style.SUCCESS("Total Rows: %s" % row_count))
            self.stdout.write(self.style.SUCCESS("Added Rows: %s" % added_rows))
            self.stdout.write(self.style.SUCCESS("Skipped Rows: %s" % skipped_rows))
