from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from web_project.fields import PercentageField
from web_project.models import BaseModel


# Create your models here.
class Vendor(BaseModel):
    wsu_discount = models.BooleanField(
        _("discount"), help_text=_("does WSU get a discount?"), default=False
    )
    discount = PercentageField(
        _("discount"),
        help_text=_("percent discount, if available"),
        max_digits=15,
        decimal_places=0,
        default=0,
    )
    website = models.URLField(_("website"), help_text=_("URL/Link to Vendor Website"))
    vendor_logo = models.ImageField(_("logo"), blank=True)
    phone = PhoneNumberField(_("phone number"), blank=True)
    street1 = models.CharField(_("address 1"), max_length=50, blank=True)
    street2 = models.CharField(
        _("address 2"), help_text=_("optional"), max_length=50, blank=True
    )
    city = models.CharField(_("city"), max_length=50, blank=True)
    state = models.ForeignKey(_("US state"), "globals.state", blank=True)
    zip = models.CharField(_("ZIP code"), max_length=10, blank=True)
    email = models.EmailField(
        _("email"), help_text=_("e.g., for main contact"), max_length=60, blank=True
    )

    class Meta:
        ordering = ["name"]

    def get_absolute_url(self):
        kwargs = {"pk": self.id, "slug": self.slug}
        return reverse("vendor_detail", kwargs=kwargs)
