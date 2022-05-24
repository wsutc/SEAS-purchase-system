import csv
import os

from click import BaseCommand
import models
from django.conf import settings

class ImportSpendCat(BaseCommand):
    def handle(self, *args, **options):
        with open(os.join.path(settings.BASE_DIR / 'cat_import.csv')) as f:
            reader = csv.reader(f)
            for row in reader:
                _, created = models.SpendCategory.object.get_or_create(
                    object = row[1],
                    subobject = row[2],
                    code = row[4],
                    description = row[5]
                )