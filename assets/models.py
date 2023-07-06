from datetime import datetime

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from djmoney.models.fields import MoneyField
from phonenumber_field.modelfields import PhoneNumberField

# from purchases.models import Manufacturer
from web_project.models import BaseModel


# Create your models here.
class AssetBaseModel(BaseModel):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_related",
        # editable=False,
    )
    modified_date = models.DateTimeField(auto_now=True, blank=True)

    class Meta:
        abstract = True


class Building(AssetBaseModel):
    name = models.CharField(_("name"), max_length=150)
    code = models.CharField(
        _("abbreviated code"),
        help_text=_("e.g. BSEL"),
        max_length=50,
    )


class Room(AssetBaseModel):
    building = models.ForeignKey(
        Building,
        verbose_name=_("building"),
        on_delete=models.PROTECT,
    )
    number = models.CharField(
        _("room number"),
        help_text=_("do not include building prefix"),
        max_length=50,
    )


class AssetCondition(models.Model):
    name = models.CharField(_("name"), max_length=50)
    description = models.TextField(_("descriptions"), blank=True)

    class Meta:
        verbose_name = _("Asset Condition")
        verbose_name_plural = _("Asset Conditions")

    def __str__(self):
        return self.name


class Manufacturer(AssetBaseModel):
    website = models.URLField(_("manufacturer website"), max_length=200)
    contact_name = models.CharField(_("contact name"), max_length=100, blank=True)
    contact_phone = PhoneNumberField(_("contact phone number"), blank=True)
    contact_extension = models.CharField(
        _("phone extension"),
        max_length=50,
        blank=True,
    )
    contact_email = models.EmailField(_("contact email"), max_length=254, blank=True)


class EnumerableAssetGroup(AssetBaseModel):
    """For assets that are often identified with a number, like calipers or power
    supplies. Smaller items may not have a true asset tag. To prevent numbers from
    getting too large, use smaller categories such as "Digital Calipers" instead of
    the generic "Calipers."
    """

    counter_digits = models.PositiveSmallIntegerField(
        _("number of digits for counter"),
        default=2,
    )
    next_digit = models.PositiveSmallIntegerField(_("next counter digit"), default=1)

    def get_next_digit(self) -> int:
        current_next_digit = self.next_digit
        new_next_digit = current_next_digit + 1
        self.next_digit = new_next_digit
        self.save()

        return current_next_digit


class Asset(AssetBaseModel):
    tag = models.CharField(
        _("asset tag"),
        help_text=_("should be a scannable barcode"),
        max_length=50,
        blank=True,
        unique=True,
    )
    capital_equipment = models.BooleanField(
        _("capital equipment"),
        help_text=_("must meet conditions"),
    )
    enumerable = models.BooleanField(
        _("enumerable"),
        help_text=_('typically used for calipers or other "countable" assets'),
    )
    enumerable_group = models.ForeignKey(
        EnumerableAssetGroup,
        verbose_name=_("enumerable group"),
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    enumerable_counter = models.CharField(
        _("enumerable counter"),
        max_length=50,
        blank=True,
    )
    enumerable_tag = models.CharField(_("enumerable tag"), max_length=50, blank=True)
    manufacturer = models.ForeignKey(
        Manufacturer,
        verbose_name=_("manufacturer"),
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    model_number = models.CharField(_("model number"), max_length=50, blank=True)
    serial_number = models.CharField(
        _("manufacturer serial number"),
        max_length=50,
        blank=True,
    )
    purchase_year = models.PositiveIntegerField(
        _("year of purchase"),
        validators=[MinValueValidator(1900), MaxValueValidator(datetime.now().year)],
        default=datetime.now().year,
    )
    principal_investigator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("principal investigator"),
        on_delete=models.PROTECT,
        related_name="principal_investigator_related",
    )
    department = models.ForeignKey(
        "purchases.Department",
        verbose_name=_("department"),
        on_delete=models.PROTECT,
    )
    primary_building = models.ForeignKey(
        Building,
        verbose_name=_("primary building"),
        on_delete=models.PROTECT,
    )
    primary_room = models.ForeignKey(
        Room,
        verbose_name=_("primary room"),
        on_delete=models.PROTECT,
    )
    condition = models.ForeignKey(
        AssetCondition,
        verbose_name=_("equipment condition"),
        on_delete=models.PROTECT,
    )
    replacement_cost_known = models.BooleanField(
        _("replacement cost known"),
        help_text=_("or estimate"),
        default=True,
    )
    replacement_cost = MoneyField(
        _("replacement cost"),
        help_text=_("may be an estimate"),
        max_digits=10,
        decimal_places=2,
        default_currency="USD",
        blank=True,
    )
    purchase_cost_known = models.BooleanField(
        _("purchase cost known"),
        help_text=_("or estimate"),
        default=True,
    )
    purchase_cost = MoneyField(
        _("original purchase cost"),
        help_text=_("may be an estimate"),
        max_digits=10,
        decimal_places=2,
        default_currency="USD",
        blank=True,
    )
    funding_source = models.CharField(_("original funding source"), max_length=50)
    federally_funded = models.BooleanField(_("federally funded"))
    end_of_life = models.PositiveIntegerField(
        _("anticipated end-of-life"),
        help_text="approximately 25 years",
        validators=[
            MinValueValidator(datetime.now().year),
            MaxValueValidator(datetime.now().year + 100),
        ],
        default=datetime.now().year + 25,
        blank=True,
    )
    comment = models.TextField(_("Remarks/Comments"), blank=True)

    def save(self, *args, **kwargs):
        if self.enumerable and self._state.adding:
            new_counter = self.enumerable_group.get_next_digit()
            padded_counter = str(new_counter).zfill(
                self.enumerable_group.counter_digits,
            )
            enumerable_name = f"{self.enumerable_group.name} #{padded_counter}"

            self.enumerable_counter = padded_counter
            self.name = enumerable_name

        self.name = (
            self.name
            if not self.enumerable
            else f"{self.enumerable_group.name} #{self.enumerable_counter}"
        )

        super().save(*args, **kwargs)


# class EnumerableAsset(AssetBaseModel):
#     """Through table for `enumerable_asset` field"""

#     name = models.CharField(_("name"), max_length=50, blank=True)
#     group = models.ForeignKey(EnumerableAssetGroup, on_delete=models.PROTECT)
#     asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
#     counter = models.CharField(
#         _("group counter"),
#         help_text=_("padded"),
#         max_length=50,
#         blank=True,
#     )

#     @property
#     def enumerable_tag(self):
#         building_code = self.asset.primary_building.code
#         room_number = self.asset.primary_room.number
#         return f"{building_code}{room_number} #{self.counter}"

#     def save(self, *args, **kwargs):
#         group = self.group
#         if self._state.adding:
#             counter_int = group.get_next_digit()
#             self.counter = str(counter_int).zfill(group.counter_digits)

#         self.name = f"{group.name} #{self.counter}"

#         super().save(*args, **kwargs)
