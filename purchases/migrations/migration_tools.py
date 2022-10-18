import random
import string

from django.db import migrations
from django.db.models import OuterRef, Subquery
from django.utils.text import slugify
from web_project.helpers import first_true


def create_manufacturer_slug(apps, schema):
    Manufacturer = apps.get_model("purchases", "Manufacturer")
    qs = Manufacturer.objects.all()
    for m in qs:
        m.slug = slugify(m.name, allow_unicode=True)

    Manufacturer.objects.bulk_update(qs, ["slug"])


def create_slugs(apps, app_name, model_name):
    print_string = []
    model = apps.get_model(app_name, model_name)
    print_string.append(f"\nModel: {model}")
    objects = model.objects.all()
    print_string.append(
        f"First object: {objects.first()} | Total Objects: {len(objects)}"
    )
    print(print_string)
    for counter, object in enumerate(objects):
        obj_print_str = [f"Object[{counter}]: {object}"]
        if hasattr(object, "name") and object.name:
            slug_raw = f"{object.name}"
            obj_print_str.append(f"name -> {slug_raw}")
        elif hasattr(object, "program_workday") and object.program_workday:
            slug_raw = f"{object.program_workday}"
            obj_print_str.append(f"program_workday -> {slug_raw}")
        elif hasattr(object, "grant") and object.grant:
            slug_raw = f"{object.grant}"
            obj_print_str.append(f"grant -> {slug_raw}")
        elif hasattr(object, "gift") and object.gift:
            slug_raw = f"{object.gift}"
            obj_print_str.append(f"gift -> {slug_raw}")
        elif hasattr(object, "description") and object.description:
            slug_raw = f"{object.description}"
            obj_print_str.append(f"description -> {slug_raw}")
        else:
            slug_raw = random.choices(string.ascii_lowercase + string.digits, k=8)
            obj_print_str.append(f"random -> {slug_raw}")

        object.slug = slugify(slug_raw, allow_unicode=True)
        obj_print_str.append(f"-> {object.slug}")
        print(obj_print_str)

    return model, objects


def create_carrier_slugs(apps, schema_editor):
    model, objects = create_slugs(apps, "purchases", "Carrier")

    count = model.objects.bulk_update(objects, ["slug"], 100)
    print(f"{count} carriers got a slug!")


def create_account_slugs(apps, schema_editor):
    model, accounts = create_slugs(apps, "purchases", "Accounts")

    count = model.objects.bulk_update(accounts, ["slug"], 100)
    print(f"{count} accounts got a slug!")


def populate_spendcat_ext(apps, schema_editor):
    PurchaseRequestAccount = apps.get_model("purchases", "purchaserequestaccount")
    ExternalSpendCategory = apps.get_model("accounts", "spendcategory")
    SpendCategory = apps.get_model("purchases", "spendcategory")

    qs = PurchaseRequestAccount.objects.all()

    # pseudo-code
    """qs.update(
        spend_category_ext = spend_category
    )"""

    # real code
    scsq = SpendCategory.objects.filter(id=OuterRef(OuterRef("spend_category_id")))
    escsq = ExternalSpendCategory.objects.filter(name__in=Subquery(scsq.values("code")))

    qs.update(spend_category_ext_id=Subquery(escsq.values("id")[:1]))


def change_account_foreign_relationship(apps, schema_editor):
    # PurchaseRequest = apps.get_model("purchases", "purchaserequest")
    PurchaseRequestAccount = apps.get_model("purchases", "purchaserequestaccount")
    PurchaseRequestAccounts = apps.get_model("purchases", "purchaserequestaccounts")
    Account = apps.get_model("accounts", "account")

    MATCH = {
        "percent": "p",
        "amount": "a",
    }

    old_account_objs = PurchaseRequestAccounts.objects.all()

    for old_account in old_account_objs:
        old_account_obj = old_account.accounts
        identity_list = [
            old_account_obj.program_workday,
            old_account_obj.grant,
            old_account_obj.gift,
        ]
        account_identity = first_true(identity_list, False)
        new_account = Account.objects.get(fund=account_identity)
        PurchaseRequestAccount.objects.create(
            purchase_request=old_account.purchase_request,
            account=new_account,
            spend_category=old_account.spend_category,
            distribution_type=MATCH[old_account.distribution_type],
            distribution_input=old_account.distribution_input,
        )


class Migration(migrations.Migration):

    dependencies = [
        (
            "purchases",
            "0049_vendor_created_date_alter_manufacturer_created_date_and_more",
        )
    ]
