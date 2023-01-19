import decimal
import logging
from datetime import date
from pathlib import Path

import shortuuid
from django.conf import settings

# from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db import models, transaction
from django.db.models import Count, F, Max, Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django_listview_filters._helpers import get_setting
from djmoney.models.fields import MoneyField
from djmoney.money import Money
from furl import furl
from phonenumber_field.modelfields import PhoneNumberField

from globals.validators import PDF_EXTS
from purchases.exceptions import StatusCodeNotFound
from purchases.tracking import TrackerObject
from web_project.fields import SimplePercentageField

from .models_base import (
    Accounts,
    BaseModel,
    Carrier,
    Department,
    DocumentNumber,
    Status,
    Unit,
    Urgency,
    Vendor,
)

# from web_project.helpers import Percent


logger = logging.getLogger(__name__)
if settings.DEBUG:
    logger.setLevel("DEBUG")


class Requisitioner(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    wsu_id = models.CharField("WSU ID", max_length=50, blank=True, null=True)
    slug = models.SlugField(null=True)
    phone = PhoneNumberField("Phone Number", max_length=25, blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.PROTECT)

    class Meta:
        ordering = ["user__last_name", "user__first_name"]

    def save(self, *args, **kwargs):
        self.slug = slugify(self.user.get_full_name(), allow_unicode=True)

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        kwargs = {"slug": self.slug, "pk": self.pk}
        return reverse("requisitioner_detail", kwargs=kwargs)

    def __str__(self):
        return self.user.get_full_name()


def getsimpleattrs(object):
    """Return list of attributes of <object> that are not callable or private
    (starting with '__')

    :param object: An object with attributes
    :type object: object
    :return: List of attributes from object excluding callables or private
    (starting with '__')
    :rtype: list
    """
    variables = [
        attr
        for attr in dir(object)
        if not callable(getattr(object, attr)) and not attr.startswith("__")
    ]

    return variables


def status_code(key: int) -> str:
    """Return two-character code (lowered) (e.g. 'rc' for 'Received') given
    status key (e.g. 8).
    """
    for class_variable in getsimpleattrs(PurchaseRequest):
        if getattr(PurchaseRequest, class_variable) == key:
            return class_variable

    raise StatusCodeNotFound(key)


class PurchaseRequest(models.Model):
    log_name = "PurchaseRequest"
    id = models.AutoField(primary_key=True, editable=False)
    slug = models.SlugField(max_length=255, default="", editable=False)
    requisitioner = models.ForeignKey(Requisitioner, on_delete=models.PROTECT)
    number = models.CharField(max_length=10, blank=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, null=True)
    created_date = models.DateTimeField("Created Date", auto_now_add=True)
    need_by_date = models.DateField("Date Required (optional)", blank=True, null=True)
    tax_exempt = models.BooleanField("Tax Exempt?", default=False)
    # accounts = models.ManyToManyField(Accounts, through="PurchaseRequestAccounts")
    accounts = models.ManyToManyField(
        "accounts.account", through="PurchaseRequestAccount"
    )
    subtotal = MoneyField(
        "Subtotal", decimal_places=2, max_digits=14, default_currency="USD", default=0
    )
    shipping = MoneyField(
        "Shipping ($)",
        decimal_places=2,
        max_digits=14,
        default_currency="USD",
        default=0,
    )
    sales_tax_rate = SimplePercentageField(
        _("sales tax rate"), max_digits=10, decimal_places=4, null=True
    )
    # new_st = PercentageField(
    #     _("new sales tax"), max_digits=10, decimal_places=4, blank=True, null=True
    # )
    sales_tax = MoneyField(
        "Sales Tax ($)",
        decimal_places=2,
        max_digits=14,
        default_currency="USD",
        default=0,
    )
    grand_total = MoneyField(
        "Grand Total ($)",
        decimal_places=2,
        max_digits=14,
        default_currency="USD",
        default=0,
    )
    urgency = models.ForeignKey(Urgency, on_delete=models.PROTECT, default=1)
    justification = models.TextField("Justification", blank=False)
    instruction = models.TextField("Special Instructions")

    class Meta:
        ordering = ["-created_date"]

    class PurchaseType(models.TextChoices):
        PO = "po", _("PURCHASE ORDER")
        PCARD = "pcard", _("PCARD")
        IRI = "iri", _("IRI")
        INV_VOUCHER = "invoice voucher", _("INVOICE VOUCHER")
        CONTRACT = "contract", _("CONTRACT")

    purchase_type = models.CharField(
        "Choose One",
        choices=PurchaseType.choices,
        default=PurchaseType.PCARD,
        max_length=25,
    )

    status = models.ForeignKey(Status, on_delete=models.PROTECT)

    def get_absolute_url(self):
        kwargs = {"slug": self.slug}
        return reverse("purchaserequest_detail", kwargs=kwargs)

    def save(self, *args, **kwargs):
        if not self.number:
            doc_number, _ = DocumentNumber.objects.get_or_create(
                document="PurchaseRequest",
                defaults={
                    "prefix": "PR",
                    "padding_digits": 5,
                },
            )
            self.number = doc_number.get_next_number()
        if not self.slug:
            self.slug = slugify(self.number, allow_unicode=True)

        self.set_totals()

        logger.info(f"Model.save() sales_tax_rate: {self.sales_tax_rate}")

        super().save(*args, **kwargs)

    def get_subtotal(self):
        extended_price = SimpleProduct.objects.filter(
            purchase_request_id=self.id
        ).aggregate(Sum("extended_price", default=0))
        # if extended_price["extended_price__sum"] != None:
        #     pass
        # else:
        #     extended_price["extended_price__sum"] = 0
        return Money(extended_price["extended_price__sum"], "USD")

    def get_taxable_subtotal(self):
        extended_price = (
            SimpleProduct.objects.filter(purchase_request_id=self.id)
            .filter(taxable=True)
            .aggregate(Sum("extended_price", default=0))
        )
        # if extended_price["extended_price__sum"] != None:
        #     pass
        # else:
        #     extended_price["extended_price__sum"] = 0
        return Money(extended_price["extended_price__sum"], "USD")

    def set_totals(self):
        """Set totals for purchase request; does NOT save

        :return: tuple of subtotal, sales tax, grand total
        """
        log_name = f"{self.log_name}.set_totals"
        self.subtotal = self.get_subtotal()
        taxable_subtotal = self.get_taxable_subtotal()
        logger.debug(f"{log_name}.sales_tax_rate: {self.sales_tax_rate}")
        logger.debug(f"{log_name}.sales_tax_rate type: {type(self.sales_tax_rate)}")
        taxable_amount = taxable_subtotal + self.shipping
        logger.debug(f"{log_name}.taxable_amount: {taxable_amount}")
        logger.debug(f"{log_name}.taxable_amount type: {type(taxable_amount)}")

        # Money's __mul__ method uses moneyed's `force_decimal` method
        # which does `Decimal(str(other))`
        # Since str(Percent()) includes '%', the following line fails unless
        # '.value' is added
        # if isinstance(self.sales_tax_rate, Percent):
        #     tax_rate = self.sales_tax_rate.value
        # else:
        tax_rate = self.sales_tax_rate
        sales_tax_raw = taxable_amount * tax_rate
        self.sales_tax = round(sales_tax_raw, 2)

        self.grand_total = self.subtotal + self.shipping + self.sales_tax

        return self.subtotal, self.sales_tax, self.grand_total

    def update_totals(self):
        qs = PurchaseRequest.objects.filter(pk=self.pk)

        totals = qs.first().set_totals()

        qs.update(
            subtotal=totals[0],
            sales_tax=totals[1],
            grand_total=totals[2],
        )
        return totals

    # def sales_tax_display(self):
    #     percent = self.sales_tax_rate * 100
    #     return "%s" % percent

    # def update_transactions(self):
    #     if self.purchaserequestaccounts_set.first():
    #         grand_total = self.grand_total
    #         account = self.purchaserequestaccounts_set.first().accounts
    #         balance, _ = Balance.objects.get_or_create(
    #             account=account, defaults={"balance": 0, "starting_balance": 0}
    #         )
    #         transaction, created = Transaction.objects.get_or_create(
    #             purchase_request=self,
    #             defaults={"total_value": grand_total, "balance": balance},
    #         )
    #         if not created:
    #             transaction.total_value = -grand_total
    #             transaction.save()

    def get_tracking_link(self):
        if stub := self.carrier.tracking_link:
            return stub + self.tracking_number
        else:
            return None

    def __str__(self):
        return self.number


def vendor_order_attachments_path(instance, filename):
    file_extension = Path(filename).suffix

    new_filename = shortuuid.uuid()
    today = date.today()
    year = today.strftime("/%Y")
    month = today.strftime("/%m")

    rpath = f"uploads/{year}/{month}/{new_filename}{file_extension}"

    return rpath


class VendorOrder(BaseModel):
    name = models.CharField(verbose_name=_("order number"), max_length=50)
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, blank=False)
    link = models.URLField(verbose_name=_("link"), blank=True)
    approved_request = models.FileField(
        _("approved purchase request"),
        help_text=_("pdf"),
        upload_to=vendor_order_attachments_path,
        validators=[FileExtensionValidator(PDF_EXTS)],
        blank=True,
    )

    purchase_requests = models.ManyToManyField(
        PurchaseRequest, verbose_name=_("purchase_requests")
    )
    subtotal = MoneyField(
        _("subtotal"), max_digits=14, default_currency="USD", default=0
    )
    shipping = MoneyField(
        _("shipping"), max_digits=14, default_currency="USD", default=0
    )
    sales_tax = MoneyField(
        _("sales tax"), max_digits=14, default_currency="USD", default=0
    )
    order_placed = models.DateField(_("date order placed"), blank=True)
    invoice_number = models.CharField(_("invoice number"), max_length=50, blank=True)
    invoice_due_date = models.DateField(_("invoice due date"), blank=True, null=True)
    notes = models.TextField(
        _("notes"), help_text=_("what has or hasn't been received, etc."), blank=True
    )

    @property
    def grand_total(self) -> Money:
        items = [self.subtotal, self.shipping, self.sales_tax]
        math_sum = sum(items)
        return math_sum

    # @property
    # def trackers(self):
    #     model_name = "tracker"

    #     trackers = []

    #     try:
    #         tm = self._meta.app_config
    #         tracker_model = tm.get_model(model_name)
    #     except LookupError:
    #         logger.error(
    #             _("No model of {modelname} found.".format(modelname=model_name))
    #         )
    #     except:
    #         logger.error(_("Some Unknown Error"), exc_info=1)
    #         raise
    #     else:
    #         trackers = tracker_model.objects.filter(
    #             purchase_request__in=self.purchase_requests.all()
    #         )

    #     return trackers

    # @property
    # def items(self, **kwargs):
    #     model_name = "trackeritem"

    #     items = []

    #     try:
    #         app_config = self._meta.app_config
    #         trackeritem_model = app_config.get_model(model_name)
    #     except LookupError:
    #         logger.error(
    #             _("No model of {modelname} found.".format(modelname=model_name))
    #         )
    #     except:
    #         logger.error(_("Some Unknown Error"), exc_info=1)
    #         raise
    #     else:
    #         items = trackeritem_model.objects.filter(tracker__in=self.trackers)

    #     return items

    class Meta:
        verbose_name = _("vendor order")
        verbose_name_plural = _("vendor orders")
        ordering = ["-order_placed", "-created_date"]

    def save(self, *args, **kwargs):
        self.order_placed = (
            self.order_placed if self.order_placed is not None else timezone.now()
        )

        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        kwargs = {
            "pk": self.pk,
            "slug": self.slug,
        }
        return reverse("vendororder_detail", kwargs=kwargs)

    def __str__(self):
        custom_str = "{vendor} {number}".format(
            vendor=self.vendor.name, number=self.name
        )
        return custom_str


class RankManager(models.Manager):
    def move(self, obj, new_rank):
        if new_rank < 1:
            raise ValueError("Unable to set rank below '1'; already highest rank.")
        elif new_rank == obj.get_next_rank():
            raise ValueError(
                f"Unable to set rank above '{obj.rank}'; already lowest rank."
            )

        qs = self.get_queryset()
        current_rank = obj.rank  # set temp variable for filters below
        # obj.rank = 0
        qs.filter(pk=obj.pk).update(
            rank=0
        )  # avoid unique constraint (no values should be zero)

        with transaction.atomic():
            if current_rank > int(new_rank):
                qs.filter(
                    parent_model=obj.parent_model,
                    rank__lt=current_rank,
                    rank__gte=new_rank,
                ).exclude(pk=obj.pk,).order_by("-rank").update(
                    rank=F("rank") + 1,
                )
            else:
                qs.filter(
                    parent_model=obj.parent_model,
                    rank__lte=new_rank,
                    rank__gt=current_rank,
                ).exclude(pk=obj.pk,).update(
                    rank=F("rank") - 1,
                )

        obj.rank = new_rank
        obj.save()

    def create(self, **kwargs):
        instance = self.model(**kwargs)

        with transaction.atomic():
            instance.rank = instance.get_next_rank()
            instance.save()

            return instance

    def move_to_end(self, obj):
        current_rank = obj.rank

        if (obj.get_next_rank() - 1) == current_rank:
            raise ValueError(
                f"Unable to move to end; '{current_rank}' already lowest rank."
            )

        qs = self.get_queryset()

        with transaction.atomic():
            qs.filter(pk=obj.pk).update(rank=obj.get_next_rank())

            # if current_rank == obj.rank: raise ValueError("Unable to move to end; '{}'
            #     already lowest rank.".format(current_rank))

            qs.filter(parent_model=obj.parent_model, rank__gt=current_rank,).order_by(
                "rank"
            ).update(rank=F("rank") - 1)

    def move_to_top(self, obj):
        if obj.rank == 1:
            raise ValueError("Unable to set rank below '1'; already highest rank.")

        current_rank = obj.rank

        qs = self.get_queryset()

        with transaction.atomic():
            qs.filter(pk=obj.pk).update(rank=0)

            qs.filter(parent_model=obj.parent_model, rank__lt=current_rank,).order_by(
                "-rank"
            ).update(rank=F("rank") + 1)

    def normalize_ranks(self, field: str, model: str = None):
        if model in self.model.StatusModel.choices:
            model_list = [model]
        else:
            model_list = self.model.StatusModel.choices

        qs = self.get_queryset()

        qsa = self.model.objects.none()

        with transaction.atomic():
            for m in model_list:
                kwargs = {field: m[0]}
                qsm = qs.filter(**kwargs).order_by("rank")
                result = qsm.aggregate(Max("rank"), Count("rank"))

                if (
                    result["rank__max"] == result["rank__count"]
                    or result["rank__count"] == 0
                ):
                    continue

                for count, s in enumerate(qsm, 1):
                    s.rank = count + int(result["rank__max"])
                self.bulk_update(qsm, ["rank"])

                qsm.update(
                    rank=F("rank") - int(result["rank__max"]),
                )

                qsa = qsa | qsm

        for obj in qsa:
            print(f"Rank[{obj.name}]: {obj.rank}")

        # self.bulk_update(qsa, ["rank"])


class SimpleProduct(models.Model):
    name = models.CharField(max_length=100)
    purchase_request = models.ForeignKey(PurchaseRequest, on_delete=models.CASCADE)
    manufacturer = models.CharField(
        "Manufacturer (optional)", max_length=50, blank=True, null=True
    )
    identifier = models.CharField(
        "Part Number/ASIN/etc.", max_length=50, blank=True, null=True
    )
    link = models.URLField(blank=True, null=True)
    unit_price = models.DecimalField(max_digits=14, decimal_places=4)
    quantity = models.DecimalField(max_digits=14, decimal_places=3, default=1)
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, default=1)
    extended_price = MoneyField(
        max_digits=14, decimal_places=2, default_currency="USD", blank=True
    )
    taxable = models.BooleanField(_("taxable"), default=True)
    rank = models.SmallIntegerField(_("in pr ordering"), editable=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("purchase_request", "identifier", "name"),
                name="unique_purchase_request_part_number",
            )
        ]

    def extend_price(self):
        extended_price = self.quantity * self.unit_price
        return extended_price

    def save(self, *args, **kwargs):
        self.extended_price = self.extend_price()

        # self.purchase_request.update_totals()

        if self._state.adding:
            self.rank = self.get_next_rank()

        super().save(*args, **kwargs)

    def get_next_rank(self):
        results = self.__class__.objects.filter(
            purchase_request=self.purchase_request,
        ).aggregate(Max("rank"))

        current_order = results["rank__max"]
        current_order = current_order if current_order else 0

        value = current_order + 1
        return value

    @property
    def vendor(self):
        vendor = self.purchase_request.vendor
        return vendor

    def __str__(self):
        name = self.name
        return name


# class Shipment(BaseModel):
#     order = models.ForeignKey(VendorOrder, on_delete=models.PROTECT)
#     # tracker = models.ForeignKey(
#     #     Tracker, on_delete=models.SET_NULL, blank=True, null=True
#     # )
#     item = models.ManyToManyField(SimpleProduct, through="ShipmentSimpleProduct")


class Tracker(models.Model):
    id = models.CharField(max_length=100, primary_key=True, editable=False, null=False)
    active = models.BooleanField(default=True)
    carrier = models.ForeignKey(
        Carrier, on_delete=models.PROTECT, blank=True, null=True
    )
    tracking_number = models.CharField(max_length=100)
    events = models.JSONField(default=None, blank=True, null=True)
    events_hash = models.CharField(max_length=100, editable=False, null=True)
    shipment_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)
    sub_status = models.CharField(max_length=50, editable=False, null=True)
    delivery_estimate = models.DateTimeField(blank=True, null=True)
    purchase_request = models.ForeignKey(
        PurchaseRequest, on_delete=models.CASCADE, null=True
    )
    # order_shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, null=True)
    earliest_event_time = models.DateTimeField(blank=True, null=True, editable=False)
    received = models.BooleanField(_("package received"), default=False)
    # simple_product = models.ManyToManyField(
    #     SimpleProduct, verbose_name=_("items"), through="TrackerItem"
    # )
    note = models.TextField(
        _("note"), help_text=_("which items, how many, etc."), blank=True
    )

    @property
    def latest_event(self):
        latest_event = self.trackingevent_set.latest()
        return latest_event

    class Meta:
        indexes = [models.Index(fields=["id"])]
        constraints = [
            models.UniqueConstraint(
                fields=("tracking_number", "carrier"),
                name="unique_tracking_number_carrier",
            )
        ]
        ordering = ["-earliest_event_time", "-purchase_request__number"]

    def get_absolute_url(self):
        kwargs = {"pk": slugify(self.id, allow_unicode=True).upper()}
        return reverse("tracker_detail", kwargs=kwargs)

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.id = self.tracking_number
        super().save(*args, **kwargs)

    def get_tracking_link(self):
        tracking_patterns = get_setting("TRACKER_PARAMS", ["trackingnumber"])

        try:
            path = furl(self.carrier.tracking_link)

            tracking_param = [
                param for param in path.args if param.lower() in tracking_patterns
            ]

            if len(tracking_param) == 1:
                path.args[tracking_param[0]] = self.tracking_number
            else:
                raise KeyError(path)

            return path.url
        except Exception:
            return None

    def update_tracker_fields(self, tracker_obj: TrackerObject) -> bool:
        """Updates <tracker> using <fields>"""
        # using `queryset.update` prevents using `model.save`, therefore, no `post_save`
        # signal
        qs = Tracker.objects.filter(pk=self.pk)

        update_fields = (
            {}
        )  # create a dict of fields with values to send to the ``.update` method
        if self.status != tracker_obj.status:
            update_fields["status"] = tracker_obj.status

        if self.sub_status != tracker_obj.sub_status:
            update_fields["sub_status"] = tracker_obj.sub_status

        if delivery_estimate := tracker_obj.delivery_estimate:
            delivery_estimate = tracker_obj.delivery_estimate
        else:
            delivery_estimate = None

        if self.delivery_estimate != delivery_estimate:
            update_fields["delivery_estimate"] = delivery_estimate

        if tracker_obj.carrier_code:
            carrier, _ = Carrier.objects.get_or_create(
                carrier_code=tracker_obj.carrier_code,
                defaults={"name": tracker_obj.carrier_name},
            )
            update_fields["carrier"] = carrier

        if len(update_fields):
            count = qs.update(**update_fields)
            return count > 0
        else:
            return False

    def create_events(self, events) -> tuple[list, list]:
        created_events = []
        updated_events = []
        set_first_time = False
        if not self.earliest_event_time:
            set_first_time = True

        for event in events:
            event_object, created = TrackingEvent.objects.update_or_create(
                tracker=self,
                time_utc=event["time_utc"],
                location=event["location"],
                defaults={"description": event["description"], "stage": event["stage"]},
            )

            if created:
                created_events.append(event_object)
            else:
                updated_events.append(event_object)

        if set_first_time:
            tracker = self.__class__.objects.filter(pk=self.pk)
            time = self.trackingevent_set.earliest().time_utc
            tracker.update(earliest_event_time=time)

        return (created_events, updated_events)

    def __str__(self):
        value = f"{self.carrier} {self.tracking_number}"
        return str(value)

    def stop(self):
        tracker = self.__class__.objects.filter(pk=self.pk)

        return bool(tracker.update(active=False))


class TrackingEvent(models.Model):
    tracker = models.ForeignKey(Tracker, on_delete=models.CASCADE)
    time_utc = models.DateTimeField()
    description = models.TextField(null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    stage = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        ordering = ["-time_utc"]
        get_latest_by = ["time_utc"]

    def __str__(self):
        value = "{location}; {description}; {time}".format(
            location=self.location,
            description=self.description,
            time=self.time_utc.strftime("%c %Z"),
        )
        return value


class TrackerStatusSteps(models.Model):
    tracker_status = models.CharField(_("status"), max_length=50)
    rank = models.PositiveSmallIntegerField(
        _("rank"), help_text=_("rank in sort order"), unique=True
    )


# --------------------------------------- Accounting ----------------------------------


class Balance(models.Model):
    account = models.OneToOneField(Accounts, on_delete=models.CASCADE)
    balance = MoneyField(max_digits=14, decimal_places=2, default_currency="USD")
    updated_datetime = models.DateTimeField(auto_now_add=True)
    starting_balance = MoneyField(
        max_digits=14, decimal_places=2, default_currency="USD", default=0
    )

    def get_absolute_url(self):
        kwargs = {"pk": self.pk}
        return reverse("balances_detail", kwargs=kwargs)

    def adjust_balance(self, adjustment_amount: decimal):
        new_balance = self.balance + adjustment_amount
        self.updated_datetime = timezone.now()
        self.balance = new_balance
        self.save()
        return self.balance

    # def recalculate_balance(self):
    #     transactions_sum = Transaction.objects.filter(balance=self).aggregate(
    #         Sum("total_value")
    #     )
    #     if total_sum := transactions_sum.get("total_value__sum"):
    #         new_balance = self.starting_balance.amount + total_sum
    #     else:
    #         new_balance = self.starting_balance
    #     self.updated_datetime = timezone.now()
    #     self.balance = new_balance
    #     self.save()

    def __str__(self):
        return f"{self.account.account_title} [{self.balance.amount}]"


@receiver(post_save, sender=Balance)
def set_initial_balance(sender, instance, created, **kwargs):
    if created:
        instance.balance = instance.starting_balance
        instance.save()


# class Transaction(models.Model):
#     balance = models.ForeignKey(Balance, on_delete=models.CASCADE)
#     purchase_request = models.OneToOneField(PurchaseRequest, on_delete=models.CASCADE)
#     processed_datetime = models.DateTimeField(auto_now_add=True)
#     total_value = MoneyField(max_digits=14, decimal_places=2, default_currency="USD")

#     class Meta:
#         ordering = ["-processed_datetime"]

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.__original_total = self.total_value

#     def __str__(self):
#         return "{} | {} [{}]".format(
#             self.balance.account.account_title,
#             self.purchase_request,
#             self.total_value.amount,
#         )
