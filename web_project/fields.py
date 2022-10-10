import logging

# from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from web_project import form_fields
from web_project.helpers import Percent, is_number

# from decimal import Decimal


logger = logging.getLogger(__name__)
if settings.DEBUG:
    logger.setLevel("INFO")


class PercentageField(models.DecimalField):
    """Enter and display percentages out of 100 but store them out of 1 in db as decimals

    Because this is based on `models.DecimalField`, `decimal_places` applies to what is stored
    in the db (/1), not what is shown or typed in (/100). With that said, add two (2) to whatever
    is desired in the form for proper validation.
    """

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
        if decimal_places is not None:
            self.humanize_decimal_places = int(decimal_places) - 2
        else:
            self.humanize_decimal_places = None

        if logger.level <= 20:
            logger.info(f"Field name: {name}")
            logger.info(f"Field verbose name: {verbose_name}")
            for c, arg in enumerate(kwargs):
                logger.info(f"before args: {arg}[{c}]")

        kwargs.update(
            {
                "max_digits": max_digits,
                "decimal_places": decimal_places,
            }
        )

        if logger.level <= 20:
            for c, arg in enumerate(kwargs):
                logger.info(f"after args: {arg}[{c}]")

        super().__init__(verbose_name, name, **kwargs)

    def formfield(self, **kwargs):
        defaults = {"form_class": form_fields.PercentageField}
        kwargs.update(decimal_places=self.decimal_places)
        defaults.update(kwargs)
        return super().formfield(**defaults)

    def from_db_value(self, value, expression, connection):
        return self.to_python(value)

    def get_prep_value(self, value):
        return value.value

    def get_db_prep_value(self, value, connection, prepared=False):
        return value.value

    def to_python(self, value):
        """Return a Percent object if value is not `None` and is_number
        return `None` if value is `None` or value is not a number and cannot
        be cast as a number.
        """
        log_name = f"{self.log_name}.to_python"
        if isinstance(value, Percent) or value is None:
            logger.debug(f"{log_name} return value: {value}")
            return value
        else:
            if is_number(value):
                if isinstance(value, str):
                    value = Percent.fromform(value, self.humanize_decimal_places)
                else:
                    value = Percent(value, self.humanize_decimal_places)
                logger.debug(f"{log_name} return value: {value}")
                return value
            else:
                raise ValidationError(_("Please enter a number."))

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return "" if value is None else value.__str__

    # def pre_save(self, model_instance, add):
    #     log_name = f"{self.log_name}.pre_save"
    #     logger.debug(f"{log_name}.self: {self}")
    #     value = super().pre_save(model_instance, add)
    #     if value is None:
    #         return value

    #     logger.debug(f"{log_name}.value: {value}")
    #     if isinstance(value, Percent):
    #         logger.debug(f"{log_name} return value: {value.value}")
    #         setattr(model_instance, self.attname, value.value)
    #         return value.value
    #     else:
    #         number = Percent(value, self.humanize_decimal_places)
    #         setattr(model_instance, self.attname, number.value)

    #         logger.debug(f"{log_name} return value: {number.value}")
    #         return number.value
