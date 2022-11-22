from django.apps import apps
from django.core.management.base import BaseCommand

from web_project.helpers import sort_title


class Command(BaseCommand):
    def handle(self, *args, **options):
        Vendor = apps.get_model("purchases", "Vendor")
        all_vendors = Vendor.objects.all()

        for vendor in all_vendors:
            vendor.sort_column = sort_title(vendor.name)

        Vendor.objects.bulk_update(all_vendors, ["sort_column"])
