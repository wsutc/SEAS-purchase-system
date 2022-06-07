from django.contrib import admin

from .models import Accounts, Carrier, Department, Manufacturer, PurchaseOrderItems, PurchaseRequestAccounts, Requisitioner, SpendCategory, Urgency, Vendor, Product, PurchaseRequest, PurchaseOrder, State, PurchaseRequestItems, Unit
from import_export.admin import ImportExportModelAdmin

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

class PurchaseRequestItemInline(admin.TabularInline):
    model = PurchaseRequestItems

@admin.register(PurchaseRequest)
class PurchaseRequestAdmin(admin.ModelAdmin):
    list_display = ['requisitioner', 'requisitioner_django', 'number', 'slug']
    inlines = [PurchaseRequestItemInline]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.update_totals()

@admin.register(PurchaseRequestItems)
class PurchaseRequestItemsAdmin(admin.ModelAdmin):
    list_display = ['product','price']

class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItems

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['number','source_purchase_request','vendor']
    inlines = [PurchaseOrderItemInline]

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
class UnitsAdmin(admin.ModelAdmin):
    list_display = ['unit','abbreviation']

@admin.register(Urgency)
class UrgencyAdmin(admin.ModelAdmin):
    list_display = ['name','note']

@admin.register(Carrier)
class CarrierAdmin(admin.ModelAdmin):
    list_display = ['name']