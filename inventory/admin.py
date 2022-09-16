from django.contrib import admin

from .models import Building, Department, EquipmentAccessory, Item, Room


# Register your models here.
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ["name", "tag_prefix"]


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ["name", "prefix"]


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ["name", "building", "number"]


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ["name", "item_type"]


@admin.register(EquipmentAccessory)
class EquipmentAccessoryAdmin(admin.ModelAdmin):
    list_display = ["item", "accessory"]


# @admin.register(EquipmentConsumable)
# class EquipmentConsumableAdmin(admin.ModelAdmin):
#     list_display = ['item','consumable']
