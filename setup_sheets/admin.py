from django.contrib import admin
from purchases.models import Manufacturer

from setup_sheets.models import Material, SetupSheet, SetupSheetTool, Tool, ToolComponents

# Register your models here.
@admin.register(SetupSheet)
class SetupSheetAdmin(admin.ModelAdmin):
    list_display = ['name']

# @admin.register(Manufacturer)
# class ManufacturerAdmin(admin.ModelAdmin):
#     list_display = ['name']

@admin.register(ToolComponents)
class ToolComponentsAdmin(admin.ModelAdmin):
    list_display = ['name','tool_type']

@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ['name','manufacturer','product_number']

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(SetupSheetTool)
class SetupSheetToolAdmin(admin.ModelAdmin):
    list_display = ['setup_sheet','position']