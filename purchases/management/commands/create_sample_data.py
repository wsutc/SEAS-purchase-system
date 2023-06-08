from typing import Any
from django.db import transaction
from django.core.management.base import BaseCommand

# from factory import debug  # , create, generate_batch
from factories import (
    AccountFactory,
    UserFactory,
    PurchaseRequestFactory,
    UnitFactory,
    VendorFactory,
)

from django.contrib.auth.models import User
from purchases.models import (
    Department,
    PurchaseRequest,
    Requisitioner,
    State,
    Status,
    Unit,
    Urgency,
    Vendor,
)
from accounts.models import Account, SpendCategory

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
            m.objects.all().delete()

        User.objects.all().exclude(is_superuser=True).delete()

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
