from urllib import request
from django.contrib import admin
from django.contrib.auth.models import User

from .models import Coating, Grade, Holder, Insert, Manufacturer, Shape, Tool

class CreatedByListFilter(admin.SimpleListFilter):
    title = 'Created By'
    parameter_name = 'created-by'

    def lookups(self, request, model_admin):
        users = []
        for user in User.objects.all():
            users.append((user.pk, user.get_full_name()))

        return users

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(created_by__id=self.value())
        else:
            return queryset

class ToolInline(admin.TabularInline):
    model=Tool
    extra=0
    exclude=['created_by']

class ToolBaseAdminClass(admin.ModelAdmin):
    list_filter = ('manufacturer__name', CreatedByListFilter)

    @admin.display(description="Created By")
    def created_by_name(self, obj):
        # created_by = obj.created_by
        if obj.created_by:
            return obj.created_by.get_full_name()
        else:
            return None

    def manufacturer_name(self, obj):
        return obj.manufacturer.name

    def save_model(self, request, obj, form, change) -> None:
        obj.created_by = request.user

        super().save_model(request, obj, form, change)

# Register your models here.
@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ['name','created_by_name']
    search_fields = ['name']
    list_filter = [CreatedByListFilter]
    exclude = ['created_by']
    inlines = [ToolInline]

    @admin.display(description="Created By")
    def created_by_name(self, obj):
        # created_by = obj.created_by
        if obj.created_by:
            return obj.created_by.get_full_name()
        else:
            return None

    def save_model(self, request, obj, form, change) -> None:
        obj.created_by = request.user

        super().save_model(request, obj, form, change)

@admin.register(Insert)
class InsertAdmin(ToolBaseAdminClass):
    list_display = ['description','designation','manufacturer_name','created_by_name']
    # filter_horizontal = ['holder']

class InsertHolderInline(admin.TabularInline):
    model=Insert.holder.through
    # fk_name = 'holder'
    extra=0
    exclude=['created_by']

@admin.register(Holder)
class HolderAdmin(ToolBaseAdminClass):
    list_display = ['description','designation','manufacturer_name']
    inlines = [InsertHolderInline]

@admin.register(Tool)
class ToolAdmin(ToolBaseAdminClass):
    list_display = ['description','manufacturer_name']

class InsertInline(admin.TabularInline):
    model = Insert
    extra = 0
    exclude = ['created_by',]

class InsertPropertiesBaseClass(admin.ModelAdmin):
    list_display = ['name','abbreviation']
    search_fields = ['name','abbreviation']
    inlines = [InsertInline]

@admin.register(Grade)
class GradeAdmin(InsertPropertiesBaseClass):
    pass

@admin.register(Coating)
class CoatingAdmin(InsertPropertiesBaseClass):
    pass

@admin.register(Shape)
class ShapeAdmin(admin.ModelAdmin):
    list_display = ['name','designation']
    search_fields = ['name','designation']
    inlines = [InsertInline]

# admin.site.register(Coating)
# admin.site.register(Tool)
# admin.site.register(Holder)
# admin.site.register(Insert)
# admin.site.register(Shape)