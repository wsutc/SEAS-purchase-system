# from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from . import Accounts, PurchaseRequest, SpendCategory

# class ShipmentSimpleProduct(models.Model):
#     shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE)
#     item = models.ForeignKey(SimpleProduct, on_delete=models.CASCADE)
#     quanity = models.DecimalField(_("quantity"), max_digits=14, decimal_places=4)


class PurchaseRequestAccounts(models.Model):
    class Meta:
        verbose_name_plural = "Purchase Request Accounts"

    purchase_request = models.ForeignKey(PurchaseRequest, on_delete=models.CASCADE)
    accounts = models.ForeignKey(Accounts, on_delete=models.PROTECT)

    spend_category = models.ForeignKey(SpendCategory, on_delete=models.PROTECT)

    PERCENT = "percent"
    AMOUNT = "amount"
    DISTRIBUTION_TYPE = ((PERCENT, "Percent"), (AMOUNT, "Amount"))
    distribution_type = models.CharField(
        choices=DISTRIBUTION_TYPE, default="percent", max_length=15
    )

    distribution_input = models.FloatField(default=100)

    def __str__(self):
        return f"{self.accounts.program_workday} | {self.spend_category.code}"


class PurchaseRequestAccount(models.Model):
    purchase_request = models.ForeignKey(PurchaseRequest, on_delete=models.CASCADE)
    account = models.ForeignKey("accounts.account", on_delete=models.PROTECT)

    spend_category = models.ForeignKey(SpendCategory, on_delete=models.PROTECT)
    spend_category_ext = models.ForeignKey(
        "accounts.spendcategory", on_delete=models.PROTECT, null=True
    )

    class DistributionType(models.TextChoices):
        PERCENT = "P", _("Percent")
        AMOUNT = "A", _("Amount")

    distribution_type = models.CharField(
        choices=DistributionType.choices, default=DistributionType.PERCENT, max_length=1
    )

    distribution_input = models.FloatField(default=100)

    class Meta:
        verbose_name_plural = _("purchase request accounts")

    def __str__(self):
        return f"{self.account.fund} | {self.spend_category.code}"
