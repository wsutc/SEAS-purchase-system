# from decimal import Decimal
import random
from random import choice  # , randint  # random,

import pytz  # , mute_signals
from django.conf import settings

# from django.contrib.auth.models import User
from factory import (  # Iterator,; List,; random,; RelatedFactory,; SelfAttribute,
    Faker,
    LazyAttribute,
    LazyAttributeSequence,
    RelatedFactoryList,
    Sequence,
    SubFactory,
)
from factory.django import DjangoModelFactory

from accounts.models import Account, SpendCategory
from purchases.models import (  # Accounts,
    Department,
    PurchaseRequest,
    PurchaseRequestAccount,
    Requisitioner,
    SimpleProduct,
    State,
    Status,
    Unit,
    Urgency,
    Vendor,
)

# from django.db.models.signals import post_save


class StateFactory(DjangoModelFactory):
    class Meta:
        model = State
        exclude = ["name_base"]

    name_base = Faker("word")
    name = LazyAttributeSequence(lambda b, n: f"{b.name_base}{n}")
    abbreviation = LazyAttribute(lambda n: f"{n.name[-2:]}")


class VendorFactory(DjangoModelFactory):
    class Meta:
        model = Vendor

    name = Faker("company")
    website = Faker("uri")
    phone = Faker("phone_number")
    street1 = Faker("street_address")
    city = Faker("city")
    state = SubFactory(StateFactory)
    zip = Faker("postcode")
    email = Faker("company_email")


class SpendCategoryFactory(DjangoModelFactory):
    class Meta:
        model = SpendCategory
        exclude = ["name_base"]

    name_base = Faker("word")
    name = LazyAttributeSequence(lambda b, n: f"{b.name_base}-{n}")
    description = Faker("sentence")
    object = Faker("word")
    subobject = Faker("word")


class AccountFactory(DjangoModelFactory):
    class Meta:
        model = Account
        exclude = ["fund_base"]

    # name = LazyAttributeSequence(lambda n: "account{}".format(n))
    name = Faker("word")
    account = Faker("numerify", text="####-####")
    fund_type = Faker("random_element", elements=Account.FundType.values)
    fund_base = Faker("bothify", text="??########")
    fund = LazyAttributeSequence(lambda b, n: f"{b.fund_base}{n}")
    # account_title = Faker("sentence", nb_words=3)
    in_use = True
    starting_balance = 0
    starting_balance_datetime = Faker("date_time", tzinfo=pytz.UTC)
    current_balance = 0


class PurchaseRequestAccountFactory(DjangoModelFactory):
    class Meta:
        model = PurchaseRequestAccount

    account = Faker("random_element", elements=Account.objects.all())
    spend_category_ext = SubFactory(SpendCategoryFactory)
    distribution_type = Faker(
        "random_element",
        elements=PurchaseRequestAccount.DistributionType.values,
    )


class UnitFactory(DjangoModelFactory):
    class Meta:
        model = Unit
        # exclude = ["unit_abbr_str"]

    unit = Faker("word")
    abbreviation = LazyAttribute(lambda n: f"{n.unit[:2]}")


class SimpleProductFactory(DjangoModelFactory):
    class Meta:
        model = SimpleProduct

    name = Faker("text", max_nb_chars=25)
    link = Faker("uri")
    manufacturer = Faker("company")
    identifier = Faker("bothify", text="??-####")
    unit_price = Faker("pyfloat", right_digits=2, positive=True, max_value=10000)
    quantity = Faker("random_int", min=1, max=50)
    unit = Faker("random_element", elements=Unit.objects.all())


class UserFactory(DjangoModelFactory):
    class Meta:
        model = settings.AUTH_USER_MODEL
        exclude = "sequence"

    sequence = Sequence(lambda n: f"{n}")

    email = LazyAttribute(lambda n: f"{n.username}@test.wsu.edu")
    password = Faker("password", length=8)
    first_name = Faker("first_name")
    last_name = Faker("last_name")

    username = LazyAttribute(
        lambda n: "{}.{}{}".format(
            n.first_name.lower(),
            n.last_name.lower(),
            n.sequence,
        ),
    )

    # requisitioner = RelatedFactory(
    #     "factories.RequisitionerFactory", factory_related_name="user"
    # )


class UrgencyFactory(DjangoModelFactory):
    class Meta:
        model = Urgency
        exclude = ["name_base"]

    name_base = Faker("word")
    name = LazyAttributeSequence(lambda b, n: f"{b.name_base}{n}")

    # name = Faker("word")
    note = Faker("text", max_nb_chars=25)


class DepartmentFactory(DjangoModelFactory):
    class Meta:
        model = Department

    code = Faker("lexify", text="????")
    name = Faker("text", max_nb_chars=40)


# @mute_signals(post_save)
class RequisitionerFactory(DjangoModelFactory):
    class Meta:
        model = Requisitioner

    user = SubFactory(UserFactory, requisitioner=None)
    phone = Faker("phone_number")
    department = SubFactory(DepartmentFactory)


class StatusFactory(DjangoModelFactory):
    class Meta:
        model = Status

    name = Faker("word")
    open = Faker("pybool")
    parent_model = Faker("random_element", elements=["PR", "OR"])


class PurchaseRequestFactory(DjangoModelFactory):
    class Meta:
        model = PurchaseRequest
        exclude = ["qsr"]  # , "req"]

    # user = SubFactory(UserFactory)
    # req = Requisitioner.objects.get(user=user)

    qsr = Requisitioner.objects.all()
    print(f"Random Requisitioner: {choice(qsr)}")  # noqa: S311

    requisitioner = Faker("random_element", elements=qsr.all())
    vendor = Faker("random_element", elements=Vendor.objects.all())
    accounts = RelatedFactoryList(
        PurchaseRequestAccountFactory,
        factory_related_name="purchase_request",
        size=lambda: random.randint(1, 3),  # noqa: S311
    )
    shipping = Faker("pyfloat", right_digits=2, positive=True, max_value=100)
    sales_tax_rate = 0.087
    urgency = SubFactory(UrgencyFactory)
    justification = Faker("paragraph")
    instruction = Faker("paragraph")
    status = SubFactory(StatusFactory, parent_model=Status.StatusModel.PURCHASE_REQUEST)

    # item = RelatedFactory(
    # SimpleProductFactory, factory_related_name="purchase_request"
    # )
    items = RelatedFactoryList(
        SimpleProductFactory,
        factory_related_name="purchase_request",
        size=lambda: random.randint(1, 10),  # noqa: S311
    )
    # item2 = RelatedFactory(SimpleProductFactory, factory_related_name="number")
