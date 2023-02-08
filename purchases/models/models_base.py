"""For models with no ForeignKey relationships to other models."""
from django.db import models, transaction
from django.db.models import Count, F, Max
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from web_project.fields import SimplePercentageField
from web_project.helpers import first_true, sort_title


class BaseModel(models.Model):
    """Base model for standardization. Includes generating slug."""

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


class Status(BaseModel):
    slug = None
    created_date = None
    rank = models.PositiveSmallIntegerField(_("rank"), editable=False)
    open = models.BooleanField(
        _("open"), help_text=_("purchase request not complete"), default=False
    )

    class StatusModel(models.TextChoices):
        PURCHASE_REQUEST = "PR"
        ORDER = "OR"

    parent_model = models.CharField(
        _("model"),
        max_length=30,
        choices=StatusModel.choices,
    )

    class Meta:
        ordering = ["parent_model", "rank"]
        verbose_name_plural = _("statuses")
        verbose_name = _("status")
        constraints = [
            models.UniqueConstraint(
                fields=["parent_model", "rank"], name="status_model_unique"
            )
        ]

    objects = RankManager()

    def save(self, *args, **kwargs):
        if not self.rank:
            self.rank = self.get_next_rank()

        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        _ = super().delete(*args, **kwargs)

        self.__class__.objects.normalize_ranks("parent_model")

    def get_next_rank(self):
        results = self.__class__.objects.filter(
            parent_model=self.parent_model,
        ).aggregate(Max("rank"))

        current_order = results["rank__max"]
        current_order = current_order if current_order else 0

        value = current_order + 1
        return value


def something(something: Status):
    something.parent_model.get_quer


class Vendor(BaseModel):
    wsu_discount = models.BooleanField("Does WSU get a discount?", default=False)
    # discount_percentage = models.DecimalField(max_digits=15, decimal_places=2,
    # default=0)
    discount_percentage = SimplePercentageField(
        decimal_places=2, max_digits=15, default=0
    )
    website = models.URLField("URL/Link to Vendor Website")
    # vendor_logo = models.ImageField("Vendor Logo (optional)",blank=True)
    phone = PhoneNumberField("Vendor Phone Number", null=False, blank=True)
    street1 = models.CharField("Address 1", max_length=50, blank=True)
    street2 = models.CharField("Address 2 (optional)", max_length=50, blank=True)
    city = models.CharField("City", max_length=50, blank=True)
    state = models.ForeignKey("State", State, blank=True, null=True)
    zip = models.CharField("ZIP Code", max_length=10, blank=True)
    email = models.EmailField(max_length=60, blank=True, null=True)
    sort_column = models.CharField(max_length=50, editable=False, null=True)

    class Meta:
        ordering = ["sort_column", "name"]

    def save(self, *args, **kwargs):
        self.sort_column = sort_title(self.name)

        super().save(*args, **kwargs)

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


class Department(models.Model):
    code = models.CharField("Code/Abbreviation", max_length=10)
    name = models.CharField("Full Department Name", max_length=150)

    def __str__(self):
        return self.name


class DocumentNumber(models.Model):
    document = models.CharField(max_length=50, primary_key=True, unique=True)
    prefix = models.CharField(max_length=10, blank=True, null=True)
    padding_digits = models.IntegerField(blank=True, null=True)
    next_counter = models.IntegerField(default=1)
    last_number = models.CharField(max_length=50, editable=False, null=True)
    last_generated_date = models.DateTimeField(auto_now=True)

    def get_next_number(self):
        prefix = self.prefix
        next_counter = self.next_counter
        padded_counter = str(next_counter).zfill(self.padding_digits)
        number = f"{prefix}{padded_counter}"

        self.next_counter += 1
        self.last_number = number

        self.save()

        return number


class TrackingWebhookMessage(models.Model):
    received_at = models.DateTimeField(help_text="DateTime that message was recieved.")
    payload = models.JSONField(default=None, null=True)

    class Meta:
        indexes = [models.Index(fields=["received_at"])]


# --------------------------------------- Imported Data -------------------------------


class Accounts(BaseModel):
    name = None
    # slug = None
    account = models.CharField(
        _("account"), help_text=_("in form XXXX-XXXX."), max_length=10
    )
    budget_code = models.CharField(
        _("budget code"),
        help_text=_("usually first four characters of account"),
        max_length=5,
        blank=True,
    )
    # fund = models.CharField("Fund", max_length=5)
    grant = models.CharField(max_length=15, blank=True)
    gift = models.CharField(max_length=15, blank=True)
    program_workday = models.CharField(_("program workday"), max_length=10, blank=True)
    account_title = models.CharField(
        _("account title"),
        help_text=_("human-readable description of account"),
        max_length=200,
    )
    cost_center = models.CharField(max_length=15, null=True)

    class Meta:
        ordering = ["account"]
        constraints = [
            # models.CheckConstraint(
            #     name="%(app_label)s_%(class)s_only_one_type",
            #     check=(
            #         (
            #             (
            #                 models.Q(
            #                     grant__isnull=False,
            #                     # TODO grant__exact__not="",
            #                     gift__isnull=True,
            #                     gift__exact="",
            #                     program_workday__isnull=True,
            #                     program_workday__exact="",
            #                 )
            #                 & ~models.Q(grant_exact="")
            #             )
            #             | (
            #                 models.Q(
            #                     grant__isnull=True,
            #                     grant__exact="",
            #                     gift__isnull=False,
            #                     # TODO gift__exact="",
            #                     program_workday__isnull=True,
            #                     program_workday__exact="",
            #                 )
            #                 & ~models.Q(gift__exact="")
            #             )
            #         )
            #         | (
            #             models.Q(
            #                 grant__isnull=True,
            #                 grant__exact="",
            #                 gift__isnull=True,
            #                 gift__exact="",
            #                 program_workday__isnull=False,
            #                 # TODO program_workday__exact="",
            #             )
            #             & ~models.Q(program_workday__exact="")
            #         )
            #     ),
            # ),
            models.UniqueConstraint(
                "gift", "grant", "program_workday", name="unique_program"
            ),
            # models.UniqueConstraint("account", name="unique_account"),
        ]
        verbose_name_plural = "Accounts"
        ordering = ["account_title"]

    @property
    def identity_list(self):
        return [self.program_workday, self.grant, self.gift]

    @property
    def identity(self) -> str:
        list = [self.program_workday, self.grant, self.gift]
        value = first_true(list, True)
        return value

    def save(self, *args, **kwargs):
        # if identity := self.identity is True:
        self.slug = slugify(self.identity, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        list = [self.program_workday, self.grant, self.gift]
        value = first_true(list, True)
        value = f"{value} | {self.account_title}"
        return value


class AccountGroup(BaseModel):
    name = models.CharField(_("group name"), max_length=50, unique=True)
    accounts = models.ManyToManyField(Accounts, verbose_name=_("accounts"))

    class Meta:
        verbose_name_plural = _("account groups")
        ordering = ["name"]


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
        return "{} ({}) [{}{}]".format(
            self.code,
            self.description,
            self.object,
            self.subobject,
        )
