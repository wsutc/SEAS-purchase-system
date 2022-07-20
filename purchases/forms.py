# from decimal import Decimal
from django import forms
from purchases.models.models_data import (
    PurchaseRequest, PurchaseRequestAccounts,
    Vendor, SimpleProduct
)
from django.forms.models import inlineformset_factory

from django_select2 import forms as s2forms

class RequisitionerWidget(s2forms.Select2Widget):
    search_fields = [
        "user__icontains",
        # "user__last_name__icontains",
    ]

class VendorWidget(s2forms.Select2Widget):
    search_fields = [
        "name__icontains"
    ]

class AccountWidget(s2forms.ModelSelect2Widget):
    search_fields = [
        "account_title__icontains",
        "program_workday__icontains",
        "grant__icontains",
        "gift__icontains"
    ]

class CarrierWidget(s2forms.Select2Widget):
    search_fields = [
        "name__icontains"
    ]

class SpendCategoryWidget(s2forms.Select2Widget):
    search_fields = [
        "description__icontains",
        "code__icontains"
    ]

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
            # 'requisitioner': forms.TextInput(),
            # 'sales_tax_rate': PercentInput(),
            'requisitioner': RequisitionerWidget(attrs={'class':'select-input'}),
            'vendor': VendorWidget(attrs={'class':'select-input'}),
            'carrier': CarrierWidget(attrs={'class':'select-input'})
        }
        exclude = ['created_date','number','items','subtotal','sales_tax','grand_total','accounts','tracker']

    # def __init__(self, *args, **kwargs):
    #     self.user = kwargs.pop('user')
    #     super().__init__(*args,**kwargs)
    #     self.fields['requisitioner'].initial = self.user

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
            'accounts': AccountWidget(attrs={'class':'select-account'}),
            'spend_category': SpendCategoryWidget(attrs={'class':'select-spendcat'}),
            'distribution_input': forms.TextInput(attrs={'style':'width:100%'})
        }

PurchaseRequestAccountsFormset = inlineformset_factory(
    PurchaseRequest,
    PurchaseRequestAccounts,
    form = PurchaseRequestAccountsForm,
    extra=1
)