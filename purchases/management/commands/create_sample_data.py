from typing import Any

from django.contrib.auth import get_user_model

# from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import models, transaction

from accounts.models import Account, SpendCategory
from assets.models import (
    Asset,
    AssetCondition,
    Building,
    EnumerableAssetGroup,
    Manufacturer,
    Room,
)

# from factory import debug  # , create, generate_batch
from factories import (
    AccountFactory,
    AssetFactory,
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

NUM_DICT = {
    "NUM_USERS": 15,
    "NUM_REQUESTS": 50,
    "NUM_UNITS": 5,
    "NUM_ACCOUNTS": 10,
    "NUM_VENDORS": 20,
    "NUM_ASSETS": 5,
}

# NUM_USERS = 15
# NUM_REQUESTS = 50
# NUM_UNITS = 5
# NUM_ACCOUNTS = 10
# NUM_VENDORS = 20

User = get_user_model()


def clear_existing_data(parent_class, model: models):
    parent_class.stdout.write(f"Current Model: {model}")
    parent_class.stdout.write(f"Count of objects to delete: {model.objects.count()}")
    if model is Requisitioner:
        qs = model.objects.all().exclude(user__is_superuser=True)
    elif model is Department:
        requisitioners = Requisitioner.objects.all()
        qs = model.objects.all().exclude(requisitioner__in=requisitioners)
    else:
        qs = model.objects.all()

    qs.delete()


class Command(BaseCommand):
    help = "Refreshes sample data (deletes all old data!)"

    @transaction.atomic
    def handle(self, *args: Any, **options: Any) -> str | None:
        self.stdout.write("Deleting old data...")

        models = [
            VendorOrder,
            PurchaseRequest,
            Account,
            SpendCategory,
            Vendor,
            State,
            Requisitioner,
            Department,
            Status,
            Unit,
            Urgency,
            Asset,
            AssetCondition,
            Manufacturer,
            Room,
            Building,
            EnumerableAssetGroup,
        ]

        for model in models:
            clear_existing_data(self, model)

        # map(clear_existing_data, models)
        # for m in models:
        #     self.stdout.write(f"Current Model: {m}")
        #     self.stdout.write(f"Count of objects to delete: {m.objects.count()}")
        #     if m is Requisitioner:
        #         qs = m.objects.all().exclude(user__is_superuser=True)
        #     elif m is Department:
        #         requisitioners = Requisitioner.objects.all()
        #         qs = m.objects.all().exclude(requisitioner__in=requisitioners)
        #     else:
        #         qs = m.objects.all()

        #     qs.delete()

        call_command("loaddata", "urgency", "status")
        # call_command("loaddata", "status")

        self.stdout.write(f"First Urgency: {Urgency.objects.first()}")

        User.objects.all().exclude(is_superuser=True).delete()

        self.stdout.write("Creating NEW sample data...")

        for _ in range(NUM_DICT.get("NUM_USERS")):
            UserFactory()

        for _ in range(NUM_DICT.get("NUM_UNITS")):
            UnitFactory()

        for _ in range(NUM_DICT.get("NUM_ACCOUNTS")):
            AccountFactory()

        for _ in range(NUM_DICT.get("NUM_VENDORS")):
            VendorFactory()

        for _ in range(NUM_DICT.get("NUM_REQUESTS")):
            PurchaseRequestFactory()

        for _ in range(NUM_DICT.get("NUM_ASSETS")):
            AssetFactory()
