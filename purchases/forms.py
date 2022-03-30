from django import forms
from purchases.models import Manufacturer

class AddManufacturerForm(forms.ModelForm):
    class Meta:
        model = Manufacturer
        fields = (
            "name",
            "website",
            "created_date",
            "wsu_discount",
            "phone",
        )