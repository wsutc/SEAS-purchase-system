# from decimal import Decimal
from django import forms
from purchases.models.models_data import (
    PurchaseRequest, PurchaseRequestAccounts,
    Vendor, SimpleProduct
)
from django.forms.models import inlineformset_factory

class AddVendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = "__all__"

class NewPRForm(forms.ModelForm):
    class Meta:
        model = PurchaseRequest
        # name = 'this is a test'
        widgets = {
            'justification': forms.Textarea(attrs={'rows':2}),
            'instruction': forms.Textarea(attrs={'rows':2}),
            # 'sales_tax_rate': PercentInput(),
        }
        exclude = ['created_date','number','items','subtotal','sales_tax','requisitioner','grand_total','accounts']

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