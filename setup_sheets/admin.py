from django.contrib import admin
from purchases.models.models_metadata import Manufacturer

from setup_sheets.models import Material, Part, PartRevision, SetupSheet, SetupSheetTool, Tool, ToolComponents, Fixture

# Register your models here.
class SetupSheetToolInline(admin.TabularInline):
    model = SetupSheetTool

# class FixtureInline(admin.TabularInline):
#     model = Fixture

@admin.register(SetupSheet)
class SetupSheetAdmin(admin.ModelAdmin):
    list_display = ['name','part_number','program_name','user_full_name']
    inlines = [SetupSheetToolInline]

    def user_full_name(self, obj):
        return obj.created_by.get_full_name()
    # inlines = [FixtureInline]

    def part_number(self, obj):
        if part := obj.part:
            return part.number
        else:
            return None

# @admin.register(Manufacturer)
# class ManufacturerAdmin(admin.ModelAdmin):
#     list_display = ['name']

class PartRevisionInline(admin.TabularInline):
    model = PartRevision
    extra = 1

class SetupSheetInline(admin.TabularInline):
    model = SetupSheet
    extra = 0
    # fields = (
    #     'name',
    #     'part_revision',
    #     'operation',
    #     'size',
    #     'created_by'
    # )

    # def user_full_name(self, obj):
    #     return obj.created_by.get_full_name()

@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ['number','name','material']
    inlines = [PartRevisionInline,SetupSheetInline]

@admin.register(PartRevision)
class PartRevisionAdmin(admin.ModelAdmin):
    list_display = ['part_number','revision']
    inlines = [SetupSheetInline]

    def part_number(self, obj):
        if part := obj.part:
            return part.number
        else:
            return None

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

@admin.register(Fixture)
class FixtureAdmin(admin.ModelAdmin):
    list_display = ['name']