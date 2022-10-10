import logging
import re
from decimal import Decimal

from django import forms
from django.conf import settings

from web_project.helpers import Percent, is_number

logger = logging.getLogger(__name__)
if settings.DEBUG:
    logger.setLevel("DEBUG")


class PercentageFieldOld(forms.DecimalField):
    log_name = "PercentageField"

    # def clean(self, value):
    #     log_name = f"{self.log_name}.clean"
    #     logger.debug(f"{log_name} value: {value}")
    #     logger.debug(f"{log_name} decimal_places: {self.decimal_places}")
    #     val = super().clean(value)

    #     logger.debug(f"{log_name} after clean value: {val}")
    #     logger.debug(f"{log_name} after clean value type: {type(val)}")

    #     if not isinstance(val, Percent):
    #         val_str = re.sub(r"[^0-9.]", "", str(val))

    #         logger.debug(f"{log_name} val_str: {val_str}")

    #         if val_str.count(".") > 1:
    #             raise ValueError(f"Invalid percent input '{value}'; too many '.'.")

    #         val = Decimal(val_str)
    #         val = Percent(val)

    #         logger.info(f"{log_name} return value: {val}")

    #     return val

    def to_python(self, value):
        log_name = f"{self.log_name}.to_python"
        logger.debug(f"{log_name} value: {value}")
        val = super().to_python(value)
        logger.debug(f"PercentageField.to_python.val: {val}")
        logger.debug(f"PercentageField.to_python.val type: {type(val)}")
        if isinstance(val, Percent):
            return val.value
        elif is_number(val):
            new_val = Percent.fromform(val)

            logger.debug(
                f"PercentageField.to_python is_number Percent: {new_val.value}"
            )

            return new_val.value
        else:
            return val

    def prepare_value(self, value):
        logger.debug(f"PercentageField.prepare_value.value: {value}")
        val = super().prepare_value(value)
        logger.debug(f"PercentageField.prepare_value.val: {val}")
        logger.debug(f"PercentageField.prepare_value.val type: {type(val)}")
        if isinstance(val, Percent):
            return val.per_hundred
        elif is_number(val):
            if isinstance(val, str):
                new_val = Percent.fromform(val)
                logger.debug(
                    f"PercentageField.prepare_value is_number is string Percent: {new_val}"
                )
                return new_val.per_hundred
            else:
                return Percent(val).per_hundred
        else:
            return val


class PercentageField(forms.DecimalField):
    log_name = "PercentageField"

    def to_python(self, value):
        log_name = f"{self.log_name}.to_python"
        logger.debug(f"{log_name} value: {value}")
        val = super().to_python(value)
        logger.debug(f"PercentageField.to_python.val: {val}")
        logger.debug(f"PercentageField.to_python.val type: {type(val)}")
        if isinstance(val, Percent):
            return val
        elif is_number(val):
            new_val = Percent.fromform(val)

            logger.debug(f"PercentageField.to_python is_number Percent: {new_val}")

            return new_val
        else:
            return val

    # def prepare_value(self, value):
    #     logger.debug(f"PercentageField.prepare_value.value: {value}")
    #     val = super().prepare_value(value)
    #     logger.debug(f"PercentageField.prepare_value.val: {val}")
    #     logger.debug(f"PercentageField.prepare_value.val type: {type(val)}")
    #     if isinstance(val, Percent):
    #         return val.per_hundred
    #     elif is_number(val):
    #         if isinstance(val, str):
    #             new_val = Percent.fromform(val)
    #             logger.debug(
    #                 f"PercentageField.prepare_value is_number is string Percent: {new_val}"
    #             )
    #             return new_val.per_hundred
    #         else:
    #             return Percent(val).per_hundred
    #     else:
    #         return val
