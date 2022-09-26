from decimal import Decimal

from django import forms
from django.db import models
from django.utils.translation import gettext_lazy as _


class PercentageField(models.DecimalField):
    """Enter and display percentages out of 100 but store them out of 1 in db as decimals"""

    description = _(
        "percentage (max {max_digits} digits; {decimal_places} decimal places"
    )

    def __init__(
        self,
        verbose_name=None,
        name=None,
        max_digits=None,
        decimal_places=None,
        **kwargs,
    ):
        self.human_decimal_places = decimal_places
        decimal_places = int(decimal_places) + 2

        kwargs.update(
            {
                "max_digits": max_digits,
                "decimal_places": decimal_places,
            }
        )

        super().__init__(verbose_name, name, **kwargs)

    def formfield(self, **kwargs):
        defaults = {
            "max_digits": self.max_digits,
            "decimal_places": self.human_decimal_places,
            "form_class": forms.DecimalField,
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value

        number = Decimal(str(value)) * Decimal("100")

        return number

    def pre_save(self, model_instance, add):
        value = super().pre_save(model_instance, add)
        if value is None:
            return value

        number = round(Decimal(str(value)) * Decimal(".01"), self.decimal_places)
        setattr(model_instance, self.attname, number)

        return number

    def __str__(self) -> str:
        value = super().__str__()
        return value
