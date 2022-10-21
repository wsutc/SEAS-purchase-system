from django.contrib import admin
from modelclone import ClonableModelAdmin

from setup_sheets.models import (
    Fixture,
    Material,
    Part,
    PartRevision,
    SetupSheet,
    SetupSheetTool,
    Tool,
    ToolComponents,
)

# from purchases.models.models_metadata import Manufacturer


# Register your models here.
class SetupSheetToolInline(admin.TabularInline):
    model = SetupSheetTool


@admin.register(SetupSheet)
class SetupSheetAdmin(ClonableModelAdmin):
    list_display = ["name", "part_number", "program_name", "user_full_name"]
    inlines = [SetupSheetToolInline]
    search_fields = [
        "name",
        "part__number",
        "program_name",
        "created_by__first_name",
        "created_by__last_name",
    ]

    def user_full_name(self, obj):
        return obj.created_by.get_full_name()

    def part_number(self, obj):
        if part := obj.part:
            return part.number
        else:
            return None


class PartRevisionInline(admin.TabularInline):
    model = PartRevision
    extra = 1


class SetupSheetInline(admin.TabularInline):
    model = SetupSheet
    extra = 0


@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ["number", "name", "material"]
    inlines = [PartRevisionInline, SetupSheetInline]


@admin.register(PartRevision)
class PartRevisionAdmin(admin.ModelAdmin):
    list_display = ["part_number", "revision"]
    inlines = [SetupSheetInline]

    def part_number(self, obj):
        if part := obj.part:
            return part.number
        else:
            return None


@admin.register(ToolComponents)
class ToolComponentsAdmin(admin.ModelAdmin):
    list_display = ["name", "tool_type"]


@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ["name", "manufacturer", "product_number"]


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(SetupSheetTool)
class SetupSheetToolAdmin(admin.ModelAdmin):
    list_display = ["setup_sheet", "position"]


@admin.register(Fixture)
class FixtureAdmin(admin.ModelAdmin):
    list_display = ["name"]
