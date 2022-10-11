from django.contrib import admin

from partnumbers.models import Part, PartRevision, PartType


# Register your models here.
class PartRevisionInline(admin.StackedInline):
    model = PartRevision
    extra = 0


@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "number",
        "type",
        "created_date",
        "slug",
        "long_description",
    ]
    list_filter = ["type"]
    inlines = [PartRevisionInline]


@admin.register(PartType)
class PartTypeAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(PartRevision)
class PartRevisionAdmin(admin.ModelAdmin):
    list_display = ["long_description", "name", "part", "slug"]
    list_filter = ["part"]
