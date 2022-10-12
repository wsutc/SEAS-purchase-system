from django.forms import MultiWidget, Select, TextInput, Widget
from djmoney.settings import CURRENCY_CHOICES


class PleasingMoneyWidget(MultiWidget):
    template_name = "pleasinghelpers/input-field.html"

    def __init__(
        self,
        choices=CURRENCY_CHOICES,
        amount_widget=TextInput,
        currency_widget=None,
        default_currency=None,
        group_attrs=None,
        *args,
        **kwargs
    ):
        self.default_currency = default_currency
        if not currency_widget:
            currency_widget = Select(choices=choices)
        widgets = (amount_widget, currency_widget)
        super().__init__(widgets, group_attrs)

    # def decompress(self, value):
    #     if value is not None:
    #         if isinstance(value, (list, tuple)):
    #             return value
    #         return [value.amount, value.currency]
    #     return [None, self.default_currency]
