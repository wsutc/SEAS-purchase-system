from django.conf import settings
from django.db import models
from django.forms import BaseModelForm
from django.urls import reverse
from django.utils.text import slugify
from djmoney.models.fields import MoneyField

from phonenumber_field.modelfields import PhoneNumberField

# from web_project.helpers import first_true


def first_true(iterable, default=False, pred=None):
    """Returns the first true value in the iterable.

    If no true value is found, returns *default*

    If *pred* is not None, returns the first item
    for which pred(item) is true.

    """
    # first_true([a,b,c], x) --> a or b or c or x
    # first_true([a,b], x, f) --> a if f(a) else b if f(b) else x
    return next(filter(pred, iterable), default)


class BaseModel(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, editable=False)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


class Manufacturer(BaseModel):  # still used in `setup_sheets`
    name = models.CharField("Name of Manufacturer", max_length=50)
    website = models.URLField("URL of Manufacturer", blank=True)
    wsu_discount = models.BooleanField("Does WSU get a discount?", default=False)
    discount_percentage = models.FloatField(default=0)
    mfg_logo = models.ImageField(
        "Manufacturer Logo (optional)", upload_to="manufacturers", blank=True
    )
    phone = PhoneNumberField("Manufacturer Phone Number (optional)", blank=True)

    def get_absolute_url(self):
        kwargs = {"pk": self.id, "slug": self.slug}
        return reverse("manufacturer_detail", kwargs=kwargs)


class State(models.Model):
    name = models.CharField(max_length=50, unique=True)
    abbreviation = models.CharField(max_length=2, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Vendor(BaseModel):
    wsu_discount = models.BooleanField("Does WSU get a discount?", default=False)
    discount_percentage = models.FloatField(default=0)
    website = models.URLField("URL/Link to Vendor Website")
    # vendor_logo = models.ImageField("Vendor Logo (optional)",blank=True)
    phone = PhoneNumberField("Vendor Phone Number", null=False, blank=True)
    street1 = models.CharField("Address 1", max_length=50, blank=True)
    street2 = models.CharField("Address 2 (optional)", max_length=50, blank=True)
    city = models.CharField("City", max_length=50, blank=True)
    state = models.ForeignKey("State", State, blank=True, null=True)
    zip = models.CharField("ZIP Code", max_length=10, blank=True)
    email = models.EmailField(max_length=60, blank=True, null=True)

    class Meta:
        ordering = ["name"]

    def get_absolute_url(self):
        kwargs = {"pk": self.id, "slug": self.slug}
        return reverse("vendor_detail", kwargs=kwargs)


class Carrier(BaseModel):
    tracking_link = models.URLField("URL stub for tracking", blank=True)
    website = models.URLField("Carrier Website", blank=True)
    carrier_code = models.CharField(max_length=30, blank=True, null=True)


class Unit(models.Model):
    unit = models.CharField(max_length=25)
    abbreviation = models.CharField(max_length=4)

    def __str__(self):
        name = self.abbreviation
        return name


class Urgency(models.Model):
    name = models.CharField(unique=True, max_length=50)
    note = models.TextField(blank=False)

    class Meta:
        verbose_name_plural = "Urgencies"

    def __str__(self):
        name = self.name
        return name


###--------------------------------------- Imported Data -------------------------------------


class Accounts(BaseModel):
    name = None
    account = models.CharField("Account", max_length=10)
    budget_code = models.CharField("Budget Code", max_length=5)
    fund = models.CharField("Fund", max_length=5)
    grant = models.CharField(max_length=15, blank=True)
    gift = models.CharField(max_length=15, blank=True)
    program_workday = models.CharField("Program Workday", max_length=10)
    account_title = models.CharField("Account Title", max_length=200)
    cost_center = models.CharField(max_length=15, null=True)

    # identity_list = [program_workday, grant, gift]

    class Meta:
        verbose_name_plural = "Accounts"
        ordering = ["account_title"]

    @property
    def identity(self) -> str:
        list = [self.program_workday, self.grant, self.gift]
        value = first_true(list, True)
        return value

    def save(self, *args, **kwargs):
        self.slug = slugify(self.identity(), allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        list = [self.program_workday, self.grant, self.gift]
        value = first_true(list, True)
        value = "{} | {}".format(value, self.account_title)
        return value


class Department(models.Model):
    code = models.CharField("Code/Abbreviation", max_length=10)
    name = models.CharField("Full Department Name", max_length=150)

    def __str__(self):
        return self.name


class SpendCategory(BaseModel):
    class Meta:
        verbose_name_plural = "Spend Categories"
        ordering = ["code"]

    name = None
    description = models.TextField("Workday Description", blank=False)
    code = models.CharField("Workday ID", max_length=15, blank=False)
    object = models.CharField(max_length=50)
    subobject = models.CharField(max_length=50)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.code, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return "%s (%s) [%s%s]" % (
            self.code,
            self.description,
            self.object,
            self.subobject,
        )


class DocumentNumber(models.Model):
    document = models.CharField(max_length=50, primary_key=True, unique=True)
    prefix = models.CharField(max_length=10, blank=True, null=True)
    padding_digits = models.IntegerField(blank=True, null=True)
    next_counter = models.IntegerField(default=1)
    last_number = models.CharField(max_length=50, editable=False, null=True)
    last_generated_date = models.DateTimeField(auto_now=True)

    def get_next_number(self):
        prefix = self.prefix
        padding_exponent = self.padding_digits - 1
        next_counter = self.next_counter
        number = prefix + str(next_counter + (10**padding_exponent))

        self.next_counter = next_counter + 1
        self.last_number = number

        self.save()

        return number
