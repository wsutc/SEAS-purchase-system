from django import forms
from purchases.models import Manufacturer, Product, Vendor

class AddManufacturerForm(forms.ModelForm):
    class Meta:
        model = Manufacturer
        fields = (
            "name",
            "website",
            "wsu_discount",
            "discount_percentage",
            "phone",
        )

class AddVendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = (
            "name",
            "website",
            "wsu_discount",
            "discount_percentage",
            "street1",
            "street2",
            "city",
            "state",
            "zip"
        )

class AddProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = (
            "name",
            "description",
            "original_manufacturer",
            "specification",
            "spec_sheet",
            "substitution",
            "approved_substitutes",
            "approved_vendors",
            "last_price",
            "link",
            "identifier"
        )