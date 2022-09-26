from django.contrib import admin

from .models import DefaultValue, State


# Register your models here.
@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ["name", "abbreviation"]


@admin.register(DefaultValue)
class DefaultValuesAdmin(admin.ModelAdmin):
    list_display = ["name", "value", "data_type", "helper_text"]
    list_editable = ["helper_text", "data_type", "value"]
