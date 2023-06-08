from django.db import models
from django.db.models import Sum
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from djmoney.models.fields import MoneyField

from web_project.models import BaseModel


# Create your models here.
class Account(BaseModel):
    name = models.CharField(
        _("account title"),
        help_text=_("human-readable description of account"),
        max_length=200,
    )
    account = models.CharField(
        _("account"),
        help_text=_("in form XXXX-XXXX."),
        max_length=10,
        blank=True,
        null=True,
    )
    budget_code = models.CharField(
        _("budget code"),
        help_text=_("usually first four characters of account"),
        max_length=5,
        blank=True,
        null=True,
    )

    class FundType(models.TextChoices):
        GRANT = "GR"
        GIFT = "GF"
        PROGRAM = "PG"

    fund_type = models.CharField(
        _("fund type"),
        max_length=30,
        choices=FundType.choices,
        default=FundType.PROGRAM,
    )

    fund = models.CharField(
        _("fund"),
        help_text=_("e.g. PG0005301 or GF003343"),
        max_length=30,
        unique=True,
    )
    cost_center = models.CharField(max_length=15, blank=True, null=True)
    starting_balance = MoneyField(
        _("starting balance"),
        max_digits=14,
        decimal_places=2,
        default_currency="USD",
    )
    starting_balance_datetime = models.DateTimeField(
        help_text=_("date and time that starting balance is valid from")
    )

    current_balance = MoneyField(
        _("current balance"),
        max_digits=14,
        decimal_places=2,
        default_currency="USD",
    )
    changed_datetime = models.DateTimeField(auto_now=True)

    in_use = models.BooleanField(_("account in active use"), default=True)

    class Meta:
        ordering = ["account"]

    def save(self, *args, **kwargs):
        self.slug = slugify(self.fund, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        value = f"{self.fund} | {self.name}"
        return value

    def transact(self, amount: MoneyField, purchase_request) -> "Transaction":
        t, c = Transaction.objects.get_or_create(
            account=self,
            purchase_request=purchase_request,
            defaults={
                "amount": amount,
                "date_time": timezone.now(),
            },
        )
        old_amount = 0 if c else t.amount
        self.update_balance(old_amount, amount)

        if not c:
            t.amount = amount
            t.date_time = timezone.now()
            t.save()

        return t

    def update_balance(self, old: MoneyField, new: MoneyField, invert: bool = False):
        adjustment = old - new
        adjustment = -1 * adjustment if invert else adjustment
        new_balance = self.current_balance + adjustment
        self.current_balance = new_balance
        self.save()

    def calculate_aggregate(self) -> MoneyField:
        result = BaseTransaction.objects.filter(account=self).aggregate(
            Sum("amount", default=0)
        )

        result = result["amount__sum"]

        value = self.starting_balance.amount - result

        return value

    def get_absolute_url(self):
        return reverse("account_detail", kwargs={"slug": self.slug})


class AccountGroup(BaseModel):
    name = models.CharField(_("group name"), max_length=50, unique=True)
    accounts = models.ManyToManyField(Account, verbose_name=_("accounts"))

    class Meta:
        verbose_name_plural = _("account groups")
        ordering = ["name"]


class BaseTransaction(models.Model):
    """Positive values mean money has been spent, balance is decreasing"""

    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = MoneyField(
        _("amount"),
        help_text=_("positive values decrease balance, negative increase"),
        max_digits=14,
        decimal_places=2,
        default_currency="USD",
    )
    date_time = models.DateTimeField(
        _("time and date that adjustment affects balance"),
        default=timezone.now,
    )

    class Meta:
        ordering = ["date_time"]

    def __str__(self):
        return f"{self.account.fund}|{self.amount} - {self.date_time:%m/%d/%y %H:%M:%S %Z}"  # noqa: E501


class BalanceAdjustment(BaseTransaction):
    reason = models.TextField(_("reason for adjustment"), max_length=200)

    def save(self, *args, **kwargs):
        if self._state.adding:
            old_amount = 0
        else:
            old_obj = BalanceAdjustment.objects.get(pk=self.pk)
            old_amount = old_obj.amount

        self.account.update_balance(old_amount, self.amount)

        super().save(*args, **kwargs)


class Transaction(BaseTransaction):
    purchase_request = models.OneToOneField(
        "purchases.purchaserequest", on_delete=models.CASCADE
    )


class SpendCategory(BaseModel):
    name = models.CharField(_("workday ID"), unique=True, max_length=15)
    description = models.TextField(_("workday description"))
    object = models.CharField(max_length=50)
    subobject = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = _("spend categories")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.description}) [{self.object}{self.subobject}]"
