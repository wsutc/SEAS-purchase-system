from django import forms

from setup_sheets.models import PartRevision, SetupSheet

from django_select2 import forms as s2forms

class PartRevisionWidget(s2forms.Select2Widget):
    # model = PartRevision
    search_fields = [
        'revision__icontains',
        # 'part__number__icontains',
        # 'part__name__icontains',
        # 'part__material__name__icontains',
    ]
    # widget = s2forms.ModelSelect2Widget(
    #     model = PartRevision,
    #     dependent_fields = {'part': 'part'}
    # )

class PartWidget(s2forms.Select2Widget):
    search_fields = [
        'name__icontains',
        'number__icontains',
        # 'material__name__icontains',
    ]

class UserWidget(s2forms.Select2Widget):
    search_fields = [
        'first_name__icontains',
        'last_name__icontains',
    ]

    # def label_from_instance(self, obj):
    #     return obj.get_full_name()

class PartRevisionForm(forms.ModelForm):
    class Meta:
        model = PartRevision
        fields = "__all__"
        widgets = {
            'justification': forms.Textarea(attrs={'rows':2}),
            'part': PartWidget(attrs={'class':'select-input'}),
        }

class SetupSheetForm(forms.ModelForm):
    class Meta:
        model = SetupSheet
        exclude = ['tools']
        widgets = {
            'part_revision': PartRevisionWidget(attrs={'class':'select-input'}),
            'part': PartWidget(attrs={'class':'select-input'}),
            'created_by': UserWidget(attrs={'class':'select-input'}),
        }