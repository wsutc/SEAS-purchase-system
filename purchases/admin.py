from django.contrib import admin

from .models import Accounts, Department, Manufacturer, PurchaseOrderItems, Requisitioner, Vendor, Product, PurchaseRequest, PurchaseOrder, State, PurchaseRequestItems

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

@admin.register(PurchaseRequest)
class PurchaseRequestAdmin(admin.ModelAdmin):
    list_display = ['requisitioner', 'number']

@admin.register(PurchaseRequestItems)
class PurchaseRequestItemsAdmin(admin.ModelAdmin):
    list_display = ['product']

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Requisitioner)
class RequisitionerAdmin(admin.ModelAdmin):
    list_display = ['first_name','last_name','email','department']

@admin.register(Accounts)
class AccountsAdmin(admin.ModelAdmin):
    list_display = ['account']