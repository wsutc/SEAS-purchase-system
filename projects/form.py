from django import forms
from django_select2 import forms as s2forms

from .models import Project


class RequisitionerWidget(s2forms.Select2Widget):
    search_fields = [
        "user__icontains",
    ]


class CreateProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        widgets = {
            "manager": RequisitionerWidget(attrs={"class": "select-input"}),
        }
        # fields = "__all__"
        exclude = ["number"]

    # def save(self, commit: bool = True):
    #     instance = forms.ModelForm.save(self, False)

    #     old_save_m2m = self.save_m2m

    #     def save_m2m():
    #         old_save_m2m()

    #         instance.projectpurchaserequest_set.clear()
    #         for pr in self.cleaned_data["projectpurchaserequest"]:
    #             instance.projectpurchaserequest_set.add[pr]

    #     self.save_m2m = save_m2m

    #     instance.save()
    #     self.save_m2m()

    #     return instance
