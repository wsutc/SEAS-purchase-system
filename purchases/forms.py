from django import forms
from purchases.models import Manufacturer, Product, PurchaseRequest, PurchaseRequestItems, Vendor
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, Div, HTML, ButtonHolder, Submit
from django.forms.models import inlineformset_factory
from .widgets import NoCurrencyMoneyWidget

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
    # ProductFormSet = forms.formset_factory(AddProductForm, extra=3)
    # formset = ProductFormSet()
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



# class ItemFormSetHelper(FormHelper):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.form_method = 'post'
#         self.layout = Layout(
#             'product',
#         )
#         self.render_required_fields = True

class NewPRForm(forms.ModelForm):
    class Meta:
        model = PurchaseRequest
        # name = 'this is a test'
        widgets = {
            'justification': forms.Textarea(attrs={'rows':2}),
            'instruction': forms.Textarea(attrs={'rows':2})
        }
        exclude = ['created_date','number','items','subtotal','sales_tax']

    # def save(self, *args, **kwargs):
    #     print("NewPRForm save")
    #     super().save(*args, **kwargs)

class NewPRIForm(forms.ModelForm):
    class Meta:
        model = PurchaseRequestItems
        fields = (
            'product',
            'quantity',
            'price'
        )
        widgets = {
            # "product": forms.TextInput,
            #"price":  NoCurrencyMoneyWidget
            }

ItemFormSet = inlineformset_factory(
    PurchaseRequest,
    PurchaseRequestItems,
    form = NewPRIForm,
    extra=1
    )