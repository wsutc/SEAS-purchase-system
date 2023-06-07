from factory import Faker, Iterator, SubFactory  # , RelatedFactory
from factory.django import DjangoModelFactory

from purchases.models import (
    Accounts,
    PurchaseRequest,
    Requisitioner,
    SimpleProduct,
    State,
    Status,
    Unit,
    Vendor,
)


class StateFactory(DjangoModelFactory):
    class Meta:
        model = State

    name = Faker("word")
    abbreviation = Faker("lexify", text="??")


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


class AccountFactory(DjangoModelFactory):
    class Meta:
        model = Accounts

    account = Faker("numerify", text="####-####")
    program_workday = Faker("bothify", text="??########")
    account_title = Faker("sentence", nb_words=3)


class SimpleProductFactory(DjangoModelFactory):
    class Meta:
        model = SimpleProduct

    name = Faker("text", max_nb_chars=25)
    manufacturer = Faker("company")
    identifier = Faker("bothify", text="??-####")
    unit_price = Faker("pricetag")
    quantity = Faker("numerify", text="%")
    unit = Iterator(Unit.objects.all())


class PurchaseRequestFactory(DjangoModelFactory):
    class Meta:
        model = PurchaseRequest

    requisitioner = Iterator(Requisitioner.objects.all())
    vendor = SubFactory(VendorFactory)
    accounts = SubFactory(AccountFactory)
    shipping = Faker("pricetag")
    sales_tax_rate = 0.087
    justification = Faker("paragraph")
    instruction = Faker("paragraph")
    status = Iterator(Status)

    # item1 = RelatedFactory(SimpleProductFactory, factory_related_name="number")
    # item2 = RelatedFactory(SimpleProductFactory, factory_related_name="number")
