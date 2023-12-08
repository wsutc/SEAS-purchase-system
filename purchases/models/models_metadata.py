# from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from . import PurchaseRequest

# class ShipmentSimpleProduct(models.Model):
#     shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE)
#     item = models.ForeignKey(SimpleProduct, on_delete=models.CASCADE)
#     quanity = models.DecimalField(_("quantity"), max_digits=14, decimal_places=4)


class PurchaseRequestAccount(models.Model):
    purchase_request = models.ForeignKey(PurchaseRequest, on_delete=models.CASCADE)
    account = models.ForeignKey(
        "accounts.account",
        verbose_name=_("account"),
        on_delete=models.PROTECT,
    )
    spend_category_ext = models.ForeignKey(
        "accounts.spendcategory",
        verbose_name=_("spend category"),
        on_delete=models.PROTECT,
    )

    class DistributionType(models.TextChoices):
        PERCENT = "P", _("Percent")
        AMOUNT = "A", _("Amount")

    distribution_type = models.CharField(
        choices=DistributionType.choices,
        default=DistributionType.PERCENT,
        max_length=1,
    )

    distribution_input = models.FloatField(default=100)

    class Meta:
        verbose_name_plural = _("purchase request accounts")

    def __str__(self):
        return f"{self.account.fund} | {self.spend_category_ext.name}"

    def natural_key(self):
        fund = self.account.natural_key()
        spend_category = self.spend_category_ext.natural_key()
        purchase_request = self.purchase_request.natural_key()
        return f"{purchase_request}|{fund}|{spend_category}"

    natural_key.dependencies = [
        "accounts.Account",
        "accounts.SpendCategory",
        "purchases.PurchaseRequest",
    ]
