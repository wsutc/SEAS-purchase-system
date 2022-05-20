from django import forms
from purchases.models import Manufacturer, Product, PurchaseRequest, Vendor

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
        widgets = {
            'description': forms.Textarea(attrs={'rows':4}),
            'specification': forms.Textarea(attrs={'rows':8})
        }
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

class NewPRForm(forms.ModelForm):
    class Meta:
        model = PurchaseRequest
        widgets = {
            'justification': forms.Textarea(attrs={'rows':2}),
            'instruction': forms.Textarea(attrs={'rows':2})
        }
        fields = (
            "requisitioner",
            "items",
            "need_by_date",
            "tax_exempt",
            "accounts",
            "shipping",
            "justification",
            "instruction",
            "purchase_type",
            "number",
            "vendor"
        )