from bootstrap_datepicker_plus.widgets import DatePickerInput
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms.models import inlineformset_factory
from django.utils.translation import gettext_lazy as _
from django_select2 import forms as s2forms
from phonenumber_field.formfields import PhoneNumberField

from purchases.exceptions import TrackerPreviouslyRegistered, TrackerRejectedUnknownCode
from purchases.tracking import register_trackers

from .models import (
    Carrier,
    Department,
    PurchaseRequest,
    PurchaseRequestAccount,
    SimpleProduct,
    Tracker,
    Vendor,
    VendorOrder,
)

# from django.db.models import FilteredRelation, Q

# from bootstrap_modal_forms.forms import BSModalForm


class RequisitionerWidget(s2forms.Select2Widget):
    search_fields = [
        "user__icontains",
        # "user__last_name__icontains",
    ]


class VendorWidget(s2forms.Select2Widget):
    search_fields = ["name__icontains"]


class AccountWidget(s2forms.ModelSelect2Widget):
    search_fields = [
        "name__icontains",
        "fund__icontains",
    ]


class CarrierWidget(s2forms.Select2Widget):
    search_fields = ["name__icontains"]


class SpendCategoryWidget(s2forms.Select2Widget):
    search_fields = ["description__icontains", "code__icontains"]


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


class AddVendorOrderForm(forms.ModelForm):
    class Meta:
        model = VendorOrder
        fields = "__all__"


# class AddRequisitionerForm(forms.ModelForm):
#     class Meta:
#         model = Requisitioner
#         fields = "__all__"


class CreateUserForm(UserCreationForm):
    wsu_id = forms.CharField(label="WSU ID", max_length=50, required=False)
    phone = PhoneNumberField(label="Phone Number", max_length=25, required=False)
    queryset = Department.objects.order_by("name")
    department = forms.ModelChoiceField(queryset)

    class Meta:
        model = User
        fields = fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "phone",
            "wsu_id",
            "department",
            "groups",
            "password1",
            "password2",
        )


class NewPRForm(forms.ModelForm):
    class Meta:
        model = PurchaseRequest
        widgets = {
            "justification": forms.Textarea(attrs={"rows": 2}),
            "instruction": forms.Textarea(attrs={"rows": 2}),
            "requisitioner": RequisitionerWidget(attrs={"class": "select-input"}),
            "vendor": VendorWidget(attrs={"class": "select-input"}),
            # attrs={"class": "form-control select-datepicker"}), needs to be applied to
            # entire group
            "need_by_date": DatePickerInput(),
        }
        exclude = [
            "created_date",
            "number",
            "items",
            "subtotal",
            "sales_tax",
            "grand_total",
            "accounts",
            "accounts_external",
            "tracker",
            "carrier",
            "tracking_number",
        ]

    # def __init__(self, *args, **kwargs):
    #     self.user = kwargs.pop('user')
    #     super().__init__(*args,**kwargs)
    #     self.fields['requisitioner'].initial = self.user


# class CustomPurchaseRequestForm(forms.Form):
#     number = forms.CharField(label="Purchase Request Number", max_length=35)
#     requisitioner = RequisitionerWidget(attrs='class':'select-input')
#     vendor = VendorWidget(attrs={'class':'select-input'})
#     urgency = forms.ModelChoiceField(Urgency)
#     justification = forms.Textarea(attrs={'rows':2})
#     instruction = forms.Textarea(attrs={'rows':2})


class CustomPurchaseRequestForm(forms.ModelForm):
    class Meta:
        model = PurchaseRequest
        # name = 'this is a test'
        widgets = {
            "justification": forms.Textarea(attrs={"rows": 2}),
            "instruction": forms.Textarea(attrs={"rows": 2}),
            # 'requisitioner': forms.TextInput(),
            # 'sales_tax_rate': PercentInput(),
            "requisitioner": RequisitionerWidget(attrs={"class": "select-input"}),
            "vendor": VendorWidget(attrs={"class": "select-input"}),
            # 'carrier': CarrierWidget(attrs={'class':'select-input'})
        }
        exclude = [
            "created_date",
            "items",
            "subtotal",
            "sales_tax",
            "grand_total",
            "accounts",
            "tracker",
            "carrier",
            "tracking_number",
        ]


# class VendorModelForm(BSModalForm):
#     class Meta:
#         model = Vendor
#         fields = '__all__'


class SimpleProductForm(forms.ModelForm):
    class Meta:
        model = SimpleProduct
        fields = (
            "name",
            "identifier",
            "manufacturer",
            "link",
            "unit_price",
            "quantity",
            "unit",
            "taxable",
        )
        widgets = {
            "name": forms.TextInput(attrs={"style": "width:100%"}),
            "identifier": forms.TextInput(attrs={"style": "width:100%"}),
            "manufacturer": forms.TextInput(attrs={"style": "width:100%"}),
            "link": forms.URLInput(attrs={"style": "width:100%"}),
            "unit_price": forms.NumberInput(attrs={"class": "currency"}),
            "quantity": forms.NumberInput(attrs={"class": "quantity"})
            # 'specification': forms.Textarea(attrs={'rows':8})
        }


# class CustomInlineFormSet(forms.BaseInlineFormSet): """Checks that there are not two
#     items on one purchase request with the same part number/ID""" def clean(self):
#     super().clean() if any(self.errors): return products = [] for form in self.forms:
#         if self.can_delete and self._should_delete_form(form): continue product =
#         (form.cleaned_data.get('purchase_request'),form.cleaned_data.get('identifier'))
#             print("%s" % product[1]) if product in products: print("Duplicate Found")
#         raise forms.ValidationError("Part Numbers must be unique per Purchase
#         Request.") products.append(product)

#         print(products.count)

SimpleProductFormset = inlineformset_factory(
    PurchaseRequest,
    SimpleProduct,
    form=SimpleProductForm,
    extra=1,
    # formset=CustomInlineFormSet
)


class PurchaseRequestAccountForm(forms.ModelForm):
    class Meta:
        model = PurchaseRequestAccount
        fields = "__all__"
        widgets = {
            "distribution_type": forms.RadioSelect(),
            "account": AccountWidget(attrs={"class": "select-account"}),
            "spend_category_ext": SpendCategoryWidget(
                attrs={"class": "select-spendcat"}
            ),
            "distribution_input": forms.TextInput(attrs={"style": "width:100%"}),
        }


PurchaseRequestAccountFormset = inlineformset_factory(
    PurchaseRequest, PurchaseRequestAccount, form=PurchaseRequestAccountForm, extra=1
)


class SimpleProductCopyForm(forms.ModelForm):
    class Meta:
        model = SimpleProduct
        fields = {
            "purchase_request",
            "name",
            "identifier",
            "manufacturer",
            "link",
            "quantity",
            "unit_price",
        }
        widgets = {"identifier": forms.TextInput(attrs={"readonly": "readonly"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        vendor = self.instance.purchase_request.vendor

        # Reduce list of purchase requests to only those that are the same
        # vendor and exclude those that already include this item
        self.fields["purchase_request"].queryset = PurchaseRequest.objects.filter(
            vendor=vendor
        ).exclude(simpleproduct__identifier=self.instance.identifier)
        self.fields["link"].disabled
        self.fields["identifier"].disabled
        self.fields["manufacturer"].disabled

    def clean(self):
        purchase_request = self.cleaned_data.get("purchase_request")
        identifier = self.instance.identifier
        if SimpleProduct.objects.filter(
            purchase_request=purchase_request, identifier=identifier
        ).exists():
            raise forms.ValidationError(
                "Product with part number %(identifier)s already exists on \
                    Purchase Request %(purchase_request)s.",
                code="duplicate",
                params={"purchase_request": purchase_request, "identifier": identifier},
            )

        return super().clean()


class TrackerForm(forms.ModelForm):
    class Meta:
        model = Tracker
        widgets = {
            "purchase_request": PurchaseRequestWidget(attrs={"class": "select-pr"}),
            "carrier": CarrierWidget(attrs={"class": "select-carrier"}),
        }
        exclude = ["events", "shipment_id", "status", "delivery_estimate"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id-TrackerForm"
        self.helper.form_class = "simpleform"
        self.helper.form_method = "post"
        self.helper.form_action = "save"

        self.helper.add_input(Submit("save", _("save")))

    def clean(self):
        tracking_number = self.cleaned_data.get("tracking_number")
        if self.data.get("carrier"):
            carrier = self.cleaned_data.get("carrier")
        else:
            carrier = None

        if carrier:
            tracker_list = [(tracking_number, carrier.carrier_code)]
        else:
            tracker_list = [(tracking_number, None)]
        try:
            responses = register_trackers(tracker_list)
        except TrackerRejectedUnknownCode:
            raise
        except Exception:
            raise

        accepted_response = next(
            iter(responses["accepted"] or []), None
        )  # get first (only) accepted response, None if empty
        rejected_response = next(
            iter(responses["rejected"] or []), None
        )  # get first rejected response

        # check if the register was accepted or rejected
        if accepted_response:
            response_dict = accepted_response
        # if rejected, need to re-specify carrier code and set a message (assuming
        # previously registered)
        else:
            response_dict = rejected_response
            if carrier:
                # this is here to set a the carrier to the form data because a rejection
                # doesn't supply one
                response_dict["tracker"].carrier_code = carrier.carrier_code
                response_dict["tracker"].carrier_name = carrier.name
            if isinstance(rejected_response["exception"], TrackerPreviouslyRegistered):
                self.message = response_dict["message"]
            else:
                raise forms.ValidationError(
                    rejected_response["message"], rejected_response["code"]
                )

        # get carrier by code; on the off chance that there's an unrecognized code,
        # create a new carrier
        if carrier:
            self.carrier, bleh = Carrier.objects.get_or_create(
                carrier_code=response_dict["tracker"].carrier_code,
                defaults={"name": response_dict["tracker"].carrier_name},
            )
        else:
            self.carrier = None
        self.tracking_number = response_dict["tracker"].tracking_number

        return super().clean()
