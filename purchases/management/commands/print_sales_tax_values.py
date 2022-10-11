from decimal import Decimal
from inspect import getattr_static

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand

from web_project.helpers import Percent

_FIELD_NAME = "new_st"


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        PurchaseRequest = apps.get_model("purchases", "purchaserequest")

        qs = PurchaseRequest.objects.filter(slug="pr10194")

        length = len(qs)
        digits = len(str(length))

        for count, pr in enumerate(qs):
            field = PurchaseRequest._meta.get_field(_FIELD_NAME)
            print(
                f"[{str(count).zfill(digits)}] {pr} (before): {field.value_from_object(pr)}"
            )

            if pr.subtotal.amount > 0:
                sales_tax = pr.sales_tax / (pr.subtotal + pr.shipping)
            else:
                sales_tax = 0

            sales_tax = Percent(sales_tax, 2) if sales_tax else 0

            setattr(pr, _FIELD_NAME, sales_tax.value)

            pr.save(update_fields=["new_st"])

            pr.refresh_from_db()

            print(f"[{str(count).zfill(digits)}] {pr} (after): {pr.new_st}")
