from django.contrib import admin

from .models import Manufacturer, Vendor, Product, PurchaseRequest, PurchaseOrder, State

@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ['name', 'website']

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['name', 'website', 'state']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'identifier', 'approved_vendors']

@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ['name', 'abbreviation']