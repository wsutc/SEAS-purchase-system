from django import forms
from purchases.models import Transaction, Manufacturer, Product, PurchaseRequest, PurchaseRequestAccounts, Vendor, SimpleProduct
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, Div, HTML, ButtonHolder, Submit
from django.forms.models import inlineformset_factory
from bootstrap_modal_forms.forms import BSModalModelForm
# from .widgets import NoCurrencyMoneyWidget

# class AddManufacturerForm(forms.ModelForm):
#     class Meta:
#         model = Manufacturer
#         fields = (
#             "name",
#             "website",
#             "wsu_discount",
#             "discount_percentage",
#             "phone",
#         )

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

# class AddProductForm(forms.ModelForm):
#     # ProductFormSet = forms.formset_factory(AddProductForm, extra=3)
#     # formset = ProductFormSet()
#     class Meta:
#         model = Product
#         widgets = {
#             'description': forms.Textarea(attrs={'rows':4}),
#             'specification': forms.Textarea(attrs={'rows':8})
#         }
#         fields = "__all__"
#         # (
#         #     "name",
#         #     "description",
#         #     "original_manufacturer",
#         #     "specification",
#         #     "spec_sheet",
#         #     "substitution",
#         #     "approved_substitutes",
#         #     "approved_vendors",
#         #     "last_price",
#         #     "link",
#         #     "identifier"
#         # )

# class UpdateProductForm(forms.ModelForm):
#     class Meta:
#         model = Product
#         widgets = {
#             'description': forms.Textarea(attrs={'rows':4}),
#             'specification': forms.Textarea(attrs={'rows':8})
#         }
#         fields = "__all__"


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
        exclude = ['created_date','number','items','subtotal','sales_tax','requisitioner','grand_total','accounts']

    # def save(self, *args, **kwargs):
    #     print("NewPRForm save")
    #     super().save(*args, **kwargs)

# class NewPRIForm(forms.ModelForm):
#     class Meta:
#         model = PurchaseRequestItems
#         fields = (
#             'product',
#             'quantity',
#             'unit',
#             'price'
#         )
#         # widgets = {
#         #     }

# ItemFormSet = inlineformset_factory(
#     PurchaseRequest,
#     PurchaseRequestItems,
#     form = NewPRIForm,
#     extra=1
#     )

class SimpleProductForm(forms.ModelForm):
    class Meta:
        model = SimpleProduct
        fields = (
            'name',
            'identifier',
            'link',
            'unit_price',
            'quantity',
            'unit'
        )
        widgets = {
            'name': forms.TextInput(attrs={'style':'width:100%'}),
            'identifier': forms.TextInput(attrs={'style':'width:100%'}),
            'link': forms.URLInput(attrs={'style':'width:100%'}),
            'unit_price': forms.NumberInput(attrs={'class':'currency'}),
            'quantity': forms.NumberInput(attrs={'class':'quantity'})
            # 'specification': forms.Textarea(attrs={'rows':8})
        }

SimpleProductFormset = inlineformset_factory(
    PurchaseRequest,
    SimpleProduct,
    form = SimpleProductForm,
    extra=1
)

class PurchaseRequestAccountsForm(forms.ModelForm):
    class Meta:
        model = PurchaseRequestAccounts
        fields = "__all__"
        widgets = {
            'distribution_type': forms.RadioSelect(),
            'accounts': forms.Select(attrs={'style':'width:100%'}),
            'spend_category': forms.Select(attrs={'style':'width:100%'}),
            'distribution_input': forms.TextInput(attrs={'style':'width:100%'})
        }

PurchaseRequestAccountsFormset = inlineformset_factory(
    PurchaseRequest,
    PurchaseRequestAccounts,
    form = PurchaseRequestAccountsForm,
    extra=1
)

# class ItemModalForm(BSModalModelForm):
#     class Meta:
#         model = PurchaseRequestItems
#         fields = {
#             'product',
#             'quantity',
#             'unit',
#             'price',
#         }

class LedgersForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = "__all__"