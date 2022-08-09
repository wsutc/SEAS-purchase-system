from django import forms

from setup_sheets.models import PartRevision

class PartRevisionForm(forms.ModelForm):
    class Meta:
        model = PartRevision
        fields = "__all__"