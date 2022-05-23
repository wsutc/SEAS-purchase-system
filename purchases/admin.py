from django.contrib import admin

from .models import Accounts, Department, Manufacturer, PurchaseOrderItems, PurchaseRequestAccounts, Requisitioner, SpendCategory, Vendor, Product, PurchaseRequest, PurchaseOrder, State, PurchaseRequestItems, Unit

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

@admin.register(SpendCategory)
class SpendCategoryAdmin(admin.ModelAdmin):
    list_display = ['code','description']

@admin.register(PurchaseRequestAccounts)
class PurchaseRequestAccountsAdmin(admin.ModelAdmin):
    list_display = ['purchase_request']

@admin.register(Unit)
class Units(admin.ModelAdmin):
    list_display = ['unit','abbreviation']