import django_filters

from .models.models_data import PurchaseRequest


class PurchaseRequestFilter(django_filters.FilterSet):
    vendor__name = django_filters.ModelChoiceFilter()
    # requisitioner = django_filters.ModelChoiceFilter()
    # status = django_filters.ChoiceFilter()

    class Meta:
        model = PurchaseRequest
        fields = {
            "status",
            "vendor__name",
            "requisitioner",
        }
