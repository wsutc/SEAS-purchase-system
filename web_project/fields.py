import logging
from decimal import Decimal

from django import forms
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from web_project import form_fields
from web_project.helpers import Percent

logger = logging.getLogger(__name__)
# if settings.DEBUG:
#     logger.setLevel("DEBUG")


class PercentageField(models.DecimalField):
    """Enter and display percentages out of 100 but store them out of 1 in db as decimals"""

    description = _(
        "percentage (max {max_digits} digits; {decimal_places} decimal places"
    )
    log_name = "models.PercentageField"

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
        defaults = {"form_class": form_fields.PercentageField}
        defaults.update(kwargs)
        return super().formfield(**defaults)

    def from_db_value(self, value, expression, connection):
        logger.debug(f"models.PercentageField.from_db_value.value: {self} -> {value}")
        if value is None:
            return value

        number = Percent(value, decimal_places=self.human_decimal_places)

        return number

    def pre_save(self, model_instance, add):
        log_name = f"{self.log_name}.pre_save"
        logger.debug(f"{log_name}.self: {self}")
        value = super().pre_save(model_instance, add)
        if value is None:
            return value

        logger.debug(f"{log_name}.value: {value}")
        number = Percent(value, self.human_decimal_places)
        setattr(model_instance, self.attname, number.value)

        return number.value
