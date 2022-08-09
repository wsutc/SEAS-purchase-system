import csv
import os

from django.core.management.base import BaseCommand
import purchases.models
from django.conf import settings

class Command(BaseCommand):
    def handle(self, *args, **options):
        with open(os.path.join(settings.BASE_DIR, 'cat_import.csv')) as f:
            reader = csv.reader(f)
            for row in reader:
                _, created = purchases.models.SpendCategory.object.get_or_create(
                    object = row[1],
                    subobject = row[2],
                    code = row[4],
                    description = row[5]
                )