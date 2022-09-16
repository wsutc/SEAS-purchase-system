from django.conf import settings
from django.forms import Select
from djmoney.forms import MoneyWidget


class BlankWidget(Select):
    template_name = "purchases/templates/empty-widget.html"


class NoCurrencyMoneyWidget(MoneyWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, currency_widget=BlankWidget)

    def value_from_datadict(self, data, files, name):
        val = super().value_from_datadict(data, files, name)
        if val[1] is None:
            val[1] = settings.DEFAULT_CURRENCY
        return val
