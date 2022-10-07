import logging
from decimal import Decimal

from django import forms
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from web_project import form_fields
from web_project.helpers import Percent

logger = logging.getLogger(__name__)
if settings.DEBUG:
    logger.setLevel("DEBUG")


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
        field_decimal_places=None,
        **kwargs,
    ):
        logger.debug(f"self: {self}")
        logger.debug(f"verbose_name: {verbose_name}")
        logger.debug(f"name: {name}")
        logger.debug(f"max_digits: {max_digits}")
        logger.debug(f"field_decimal_places: {field_decimal_places}")
        self.field_decimal_places = field_decimal_places

        try:
            decimal_places = int(field_decimal_places) + 2
        except TypeError:
            field_type = type(field_decimal_places)
            logger.warning(f"field_decimal_places not valid type: {field_type}")
            decimal_places = 2

        kwargs = {
            "max_digits": max_digits,
            "decimal_places": decimal_places,
        }

        super().__init__(verbose_name, name, **kwargs)

        logger.debug(f"Field name: {self.name}")

    def formfield(self, **kwargs):
        defaults = {"form_class": form_fields.PercentageField}
        defaults.update(kwargs)
        return super().formfield(**defaults)

    def from_db_value(self, value, expression, connection):
        log_name = f"{self.log_name}.from_db_value"
        logger.debug(f"{log_name}.value: {self.attname} -> {value}")
        if value is None:
            return value

        try:
            number = Percent(value, field_decimal_places=self.field_decimal_places)
        except TypeError:
            field_type = type(self.field_decimal_places)
            logger.error(f"{log_name} field_decimal_places TypeError: {field_type}")
            number = Percent(value, field_decimal_places=2)

        return number

    def to_python(self, value):
        log_name = f"{self.log_name}.to_python"
        if isinstance(value, Percent) or value is None:
            return value
        else:
            try:
                logger.debug(f"{log_name} value before Percent.fromform(): {value}")
                return Percent.fromform(value, self.field_decimal_places)
            except ValueError:
                return None

    def pre_save(self, model_instance, add):
        log_name = f"{self.log_name}.pre_save"
        logger.debug(f"{log_name}.self: {self}")
        value = super().pre_save(model_instance, add)
        if value is None:
            return value

        logger.debug(f"{log_name}.value: {value}")
        if isinstance(value, Percent):
            return value.value
        else:
            number = Percent(value, self.field_decimal_places)
            setattr(model_instance, self.attname, number.value)

            return number.value
