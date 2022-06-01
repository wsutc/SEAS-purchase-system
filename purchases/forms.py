from django import forms
from purchases.models import Manufacturer, Product, PurchaseRequest, PurchaseRequestItems, Vendor
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, Div, HTML, ButtonHolder, Submit
from django.forms.models import inlineformset_factory

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

ItemFormSet = inlineformset_factory(PurchaseRequest, PurchaseRequestItems, fields=['product','quantity','price'])

class ItemFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_method = 'post'
        self.layout = Layout(
            'product',
        )
        self.render_required_fields = True

class NewPRForm(forms.ModelForm):
    class Meta:
        model = PurchaseRequest
        # name = 'this is a test'
        widgets = {
            'justification': forms.Textarea(attrs={'rows':2}),
            'instruction': forms.Textarea(attrs={'rows':2})
        }
        exclude = ['created_date','number']
        # fields = (
        #     "requisitioner",
        #     "need_by_date",
        #     "tax_exempt",
        #     "shipping",
        #     "justification",
        #     "instruction",
        #     "purchase_type",
        #     "number",
        #     "vendor"
        # )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.helper.form_class = 'row g-3'
        self.helper.form_method = 'post'
        self.helper.help_text_inline = True
        self.helper.layout = Layout(
            Div(
                Div('vendor',css_class='col-4'),
                Div('need_by_date',css_class='col-4'),
                Div('urgency',css_class='col-4'),
                css_class='row'
            ),
            Div('justification',css_class='form-group col-12'),
            Div('instruction', css_class='form-group col-12')
        )
        self.helper.add_input(Submit('submit', 'Save', css_class='btn btn-primary save'))

    
    # itemformset = ItemFormSet()

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.helper = FormHelper()
    #     self.helper.form_tag = True
    #     self.helper.form_class = 'form-horizontal'
    #     self.helper.label_class = 'col-md-3 create-label'
    #     self.helper.field_class = 'col-md-9'
    #     self.helper.form_method = 'post'
    #     # self.helper.layout = Layout(
    #     #     Div(
    #     #         Fieldset('Add Items',
    #     #             ItemFormSet('items')),
    #     #         Field('note')
    #     #     )
    #     # )
    #     self.helper.add_input(Submit('submit', 'test'))

class NewPRIForm(forms.ModelForm):
    class Meta:
        model = PurchaseRequestItems
        fields = (
            'purchase_request',
            'product',
            'quantity',
            'price'
        )