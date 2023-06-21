from typing import Any

from django.conf import settings

# from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import Account, SpendCategory

# from factory import debug  # , create, generate_batch
from factories import (
    AccountFactory,
    PurchaseRequestFactory,
    UnitFactory,
    UserFactory,
    VendorFactory,
)
from purchases.models import (
    Department,
    PurchaseRequest,
    Requisitioner,
    State,
    Status,
    Unit,
    Urgency,
    Vendor,
    VendorOrder,
)

NUM_USERS = 15
NUM_REQUESTS = 50
NUM_UNITS = 5
NUM_ACCOUNTS = 10
NUM_VENDORS = 20


class Command(BaseCommand):
    help = "Refreshes sample data (deletes all old data!)"

    @transaction.atomic
    def handle(self, *args: Any, **options: Any) -> str | None:
        self.stdout.write("Deleting old data...")

        models = [
            PurchaseRequest,
            Account,
            SpendCategory,
            VendorOrder,
            Vendor,
            State,
            Requisitioner,
            Department,
            Urgency,
            Status,
            Unit,
        ]
        for m in models:
            self.stdout.write(f"Current Model: {m}")
            self.stdout.write(f"Count of objects to delete: {m.objects.count()}")
            if m is Requisitioner:
                qs = m.objects.all().exclude(user__is_superuser=True)
            elif m is Department:
                requisitioners = Requisitioner.objects.all()
                qs = m.objects.all().exclude(requisitioner__in=requisitioners)
            else:
                qs = m.objects.all()

            qs.delete()

        settings.AUTH_USER_MODEL.objects.all().exclude(is_superuser=True).delete()

        self.stdout.write("Creating NEW sample data...")

        for _ in range(NUM_USERS):
            UserFactory()

        for _ in range(NUM_UNITS):
            UnitFactory()

        for _ in range(NUM_ACCOUNTS):
            AccountFactory()

        for _ in range(NUM_VENDORS):
            VendorFactory()

        for _ in range(NUM_REQUESTS):
            PurchaseRequestFactory()
