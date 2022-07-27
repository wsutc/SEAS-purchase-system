# from decimal import Decimal
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from purchases.models.models_data import (
    PurchaseRequest, PurchaseRequestAccounts, Requisitioner,
    Vendor, SimpleProduct
)
from django.forms.models import inlineformset_factory

from bootstrap_modal_forms.forms import BSModalForm

from phonenumber_field.formfields import PhoneNumberField

from django_select2 import forms as s2forms

from purchases.models.models_metadata import Department

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

# class AddRequisitionerForm(forms.ModelForm):
#     class Meta:
#         model = Requisitioner
#         fields = "__all__"

class CreateUserForm(UserCreationForm):
    wsu_id = forms.CharField(label='WSU ID',max_length=50,required=False)
    phone = PhoneNumberField(label='Phone Number',max_length=25,required=False)
    queryset = Department.objects.order_by('name')
    department = forms.ModelChoiceField(queryset)

    class Meta:
        model = User
        fields = fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'phone',
            'wsu_id',
            'department',
            'groups',
            'password1',
            'password2'
        )

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
        exclude = ['created_date','number','items','subtotal','sales_tax','grand_total','accounts','tracker','carrier','tracking_number']

    # def __init__(self, *args, **kwargs):
    #     self.user = kwargs.pop('user')
    #     super().__init__(*args,**kwargs)
    #     self.fields['requisitioner'].initial = self.user

class VendorModelForm(BSModalForm):
    class Meta:
        model = Vendor
        fields = '__all__'

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