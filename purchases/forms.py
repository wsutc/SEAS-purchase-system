# from decimal import Decimal
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from purchases.models.models_apis import Tracker
from purchases.models.models_data import (
    PurchaseRequest, PurchaseRequestAccounts, Requisitioner,
    Vendor, SimpleProduct
)
from django.forms.models import inlineformset_factory
from django.db.models import FilteredRelation, Q

# from bootstrap_modal_forms.forms import BSModalForm

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

class PurchaseRequestWidget(s2forms.ModelSelect2Widget):
    search_fields = [
        "number__icontains",
        "vendor__name__icontains",
        "requisitioner__user__first_name__icontains",
        "requisitioner__user__last_name__icontains",
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

# class VendorModelForm(BSModalForm):
#     class Meta:
#         model = Vendor
#         fields = '__all__'

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

class CustomInlineFormSet(forms.BaseInlineFormSet):
    """Checks that there are not two items on one purchase request with the same part number/ID"""
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        products = []
        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue
            product = (form.cleaned_data.get('purchase_request'),form.cleaned_data.get('identifier'))
            print("%s" % product[1])
            if product in products:
                print("Duplicate Found")
                raise forms.ValidationError("Part Numbers must be unique per Purchase Request.")
            products.append(product)

        print(products.count)

SimpleProductFormset = inlineformset_factory(
    PurchaseRequest,
    SimpleProduct,
    form = SimpleProductForm,
    extra=1,
    # formset=CustomInlineFormSet
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

class SimpleProductCopyForm(forms.ModelForm):
    class Meta:
        model = SimpleProduct
        fields = {
            'purchase_request',
            'name',
            'identifier',
            'link',
            'quantity',
            'unit_price'
        }
        widgets = {
            'identifier': forms.TextInput(attrs={'readonly':'readonly'})
        }

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        vendor = self.instance.purchase_request.vendor

        # Reduce list of purchase requests to only those that are the same
        # vendor but exclude those that already include this item
        self.fields['purchase_request'].queryset = (
            PurchaseRequest.objects.filter(vendor=vendor)
            .exclude(simpleproduct__identifier=self.instance.identifier)
        )
        self.fields['link'].disabled
        self.fields['identifier'].disabled

    def clean(self):
        purchase_request = self.cleaned_data.get('purchase_request')
        identifier = self.instance.identifier
        if (
            SimpleProduct.objects
            .filter(purchase_request = purchase_request,identifier=identifier)
            .exists()
        ):
            raise forms.ValidationError(
                'Product with part number %(identifier)s already exists on Purchase Request %(purchase_request)s.',
                code='duplicate',
                params={
                    'purchase_request': purchase_request,
                    'identifier': identifier
                }
            )
        
        clean = super().clean()

class TrackerForm(forms.ModelForm):
    class Meta:
        model = Tracker
        widgets = {
            'purchase_request': PurchaseRequestWidget(attrs={'class':'select-pr'}),
            'carrier': CarrierWidget(attrs={'class':'select-carrier'})
        }
        exclude = ['events','shipment_id','status','delivery_estimate']