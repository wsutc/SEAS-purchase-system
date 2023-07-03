from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Value
from django.db.models.functions import Lower, Replace
from django.utils.translation import gettext_lazy as _


class SettingsManager(models.Manager):
    def get_value(
        self,
        setting_name: str,
        default: (str | int | float) = None,
    ) -> str | int | float:
        """Return setting value given correctly spelled setting_name

        :param setting_name: Setting name, must be correctly spelled; white space and
        capitalization ignored
        :type setting_name: str
        :return: Setting value; type checking should be
        :rtype: str"""
        setting_name = "".join(setting_name.split()).lower()
        qs = self.get_queryset()
        objs = (
            qs.annotate(shortname=Replace("name", Value(" "), Value("")))
            .annotate(shortname=Lower("shortname"))
            .filter(shortname=setting_name)
        )
        if len(objs) > 0:
            obj = objs.first()
            return obj.value
        else:
            return default


class DefaultValue(models.Model):
    name = models.CharField(_("setting name"), max_length=50)
    helper_text = models.TextField(_("explanatory text"), blank=True)

    class DataType(models.TextChoices):
        FLOAT = "FLOAT", _("Float")
        TEXT = "TEXT", _("Text")
        INT = "INT", _("Integer")

    data_type = models.CharField(
        _("data type"),
        choices=DataType.choices,
        default=DataType.TEXT,
        max_length=50,
    )
    value = models.TextField(_("setting value"))

    objects = SettingsManager()

    type_field = "data_type"

    @property
    def search_name(self):
        name = self.name
        stripped_lower = "".join(name.split()).lower()
        return stripped_lower

    def clean(self) -> None:
        super().clean()

        types = self.__class__.DataType
        match self.data_type:
            case types.FLOAT:
                try:
                    self.value = float(self.value)
                except ValueError as e:
                    raise ValidationError(
                        _("'%(value)s' must be of type '%(type)s'"),
                        params={"value": self.value, "type": types.FLOAT.title()},
                    ) from e
            case types.TEXT:
                try:
                    self.value = str(self.value)
                except ValueError as e:
                    raise ValidationError(
                        _("'%(value)s' must be of type '%(type)s'"),
                        params={"value": self.value, "type": types.TEXT.title()},
                    ) from e
            case types.INT:
                try:
                    self.value = int(self.value)
                except ValueError as e:
                    raise ValidationError(
                        _("'%(value)s' must be of type '%(type)s'"),
                        params={"value": self.value, "type": types.INT.title()},
                    ) from e
            case _:
                raise ValidationError(_("uknown data type chosen"))

    def __str__(self) -> str:
        value = f"{self.name}"
        return value
