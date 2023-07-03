from django.contrib import admin
from django.http.request import HttpRequest
from shortuuid import uuid

from .models import (
    Asset,
    AssetCondition,
    Building,
    # EnumerableAsset,
    EnumerableAssetGroup,
    Manufacturer,
    Room,
)


# Register your models here.
class AssetBaseAdmin(admin.ModelAdmin):
    class Meta:
        abstract = True

    def get_changeform_initial_data(self, request: HttpRequest) -> dict[str, str]:
        dummy_tag = uuid()[:7]
        return {"created_by": request.user, "tag": dummy_tag}


# class EnumerableAssetInline(admin.TabularInline):
#     model = EnumerableAsset


class AssetInline(admin.TabularInline):
    model = Asset


@admin.register(Asset)
class AssetAdmin(AssetBaseAdmin):
    list_display = ["name", "tag", "modified_date"]
    # inlines = [EnumerableAssetInline]
    change_form_template = "admin/assets/asset/change_form.html"


@admin.register(AssetCondition)
class AssetConditionAdmin(AssetBaseAdmin):
    pass


@admin.register(Building)
class BuildingAdmin(AssetBaseAdmin):
    pass


@admin.register(Room)
class RoomAdmin(AssetBaseAdmin):
    pass


@admin.register(Manufacturer)
class ManufacturerAdmin(AssetBaseAdmin):
    pass


@admin.register(EnumerableAssetGroup)
class EnumerableAssetGroupAdmin(AssetBaseAdmin):
    inlines = [AssetInline]


# @admin.register(EnumerableAsset)
# class EnumerableAssetAdmin(AssetBaseAdmin):
#     pass
