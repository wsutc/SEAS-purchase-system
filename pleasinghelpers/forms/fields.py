# from django import forms
from django.forms import ChoiceField, DecimalField
from djmoney.forms import MoneyField
from djmoney.settings import CURRENCY_CHOICES, DECIMAL_PLACES

from .widgets import PleasingMoneyWidget


class PleasingMoneyField(MoneyField):
    def __init__(
        self,
        currency_widget=None,
        currency_choices=CURRENCY_CHOICES,
        max_value=None,
        min_value=None,
        max_digits=None,
        decimal_places=DECIMAL_PLACES,
        default_amount=None,
        default_currency=None,
        *args,
        **kwargs
    ):

        amount_field = DecimalField(
            *args,
            max_value=max_value,
            min_value=min_value,
            max_digits=max_digits,
            decimal_places=decimal_places,
            **kwargs,
        )
        currency_field = ChoiceField(choices=currency_choices)

        self.widget = PleasingMoneyWidget(
            amount_widget=amount_field.widget,
            currency_widget=currency_widget or currency_field.widget,
            default_currency=default_currency,
        )
        # The two fields that this widget comprises
        fields = (amount_field, currency_field)
        super().__init__(fields, *args, **kwargs)

        # set the initial value to the default currency so that the
        # default currency appears as the selected menu item
        self.initial = [default_amount, default_currency]
