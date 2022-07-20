from typing import Set
from django.contrib import admin

from purchases import tracking

from .models.models_metadata import (
    Accounts, Carrier, Department, DocumentNumber, Manufacturer,
    Urgency, Vendor, State, Unit
)
from .models.models_data import (
    Balance, PurchaseRequest, Transaction,
    PurchaseRequestAccounts, SimpleProduct,
    SpendCategory, Requisitioner
)
from .models.models_apis import Tracker
from .signals import create_tracker#, update_tracker
from import_export.admin import ImportExportModelAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# @admin.register(Manufacturer)
# class ManufacturerAdmin(admin.ModelAdmin):
#     list_display = ['name', 'website']

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['name', 'website', 'state']

# @admin.register(Product)
# class ProductAdmin(admin.ModelAdmin):
#     list_display = ['name', 'identifier', 'approved_vendors']

@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ['name', 'abbreviation']

class SimpleProductInline(admin.TabularInline):
    model = SimpleProduct

class PurchaseRequestAccountsInline(admin.TabularInline):
    model = PurchaseRequestAccounts
    extra = 1

# class PurchaseRequestItemInline(admin.TabularInline):
#     model = PurchaseRequestItems

@admin.action(description="Change Selected to \'Awaiting Approval\'")
def make_awaiting_approval(modeladmin, request, queryset):
    queryset.update(status='1')

@admin.action(description="Change Selected to \'Approved\'")
def make_approved(modeladmin, request, queryset):
    queryset.update(status='2')

@admin.action(description="Change Selected to \'Ordered\'")
def make_ordered(modeladmin, request, queryset):
    queryset.update(status='6')

@admin.action(description="Update Totals")
def save_requests(modeladmin, request, queryset):
    for r in queryset:
        r.update_totals()
        r.update_transactions()

@admin.action(description="Update Tracker(s)")
def update_trackers(modeladmin, request, queryset):
    tracker_list = []
    for r in queryset:
        tracker_created = create_tracker('',r)
        if tracker_created:
            r.save()
        tracker_list.append(r.tracker)
    
    if len(tracker_list) > 0:
        print("First tracker: %s" % (tracker_list[0]))
    tracking.bulk_update_tracking_details(tracker_list)

@admin.register(PurchaseRequest)
class PurchaseRequestAdmin(admin.ModelAdmin):
    list_display = ['requisitioner', 'number', 'grand_total', 'status', 'slug', 'get_tracker_status']
    inlines = [SimpleProductInline,PurchaseRequestAccountsInline]
    actions = [make_awaiting_approval,save_requests,update_trackers]

    @admin.display(description='Tracking Status')
    def get_tracker_status(self, obj):
        if obj.tracker:
            return obj.tracker.status
        return

    @admin.display(description='Update Tracker(s)')
    def update_tracker(self, obj):
        if obj.tracker:
            tracking.update_tracking_details(obj.tracker)
            return obj.tracker.status
        return

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.update_totals()

# @admin.register(PurchaseRequestItems)
# class PurchaseRequestItemsAdmin(admin.ModelAdmin):
#     list_display = ['product','price']

# class PurchaseOrderItemInline(admin.TabularInline):
#     model = PurchaseOrderItems

# @admin.register(PurchaseOrder)
# class PurchaseOrderAdmin(admin.ModelAdmin):
#     list_display = ['number','source_purchase_request','vendor']
#     inlines = [PurchaseOrderItemInline]

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name']

class RequisitionerInline(admin.StackedInline):
    model = Requisitioner

class UserAdmin(BaseUserAdmin):
    inlines = (RequisitionerInline,)

@admin.register(Requisitioner)
class RequisitionerAdmin(admin.ModelAdmin):
    list_display = ['user','department']

@admin.register(Accounts)
class AccountsAdmin(admin.ModelAdmin):
    list_display = ['account','account_title','program_workday']

@admin.register(SpendCategory)
class SpendCategoryAdmin(admin.ModelAdmin):
    list_display = ['code','description','object','subobject']

@admin.register(PurchaseRequestAccounts)
class PurchaseRequestAccountsAdmin(admin.ModelAdmin):
    list_display = ['accounts','purchase_request']

@admin.register(Unit)
class UnitsAdmin(admin.ModelAdmin):
    list_display = ['unit','abbreviation']

@admin.register(Urgency)
class UrgencyAdmin(admin.ModelAdmin):
    list_display = ['name','note']

class TrackerInline(admin.TabularInline):
    model = Tracker
    extra = 0

@admin.register(Carrier)
class CarrierAdmin(admin.ModelAdmin):
    list_display = ['name']
    inlines = [TrackerInline]

@admin.register(Tracker)
class TrackerAdmin(admin.ModelAdmin):
    list_display = ['id','shipment_id','status']

@admin.register(SimpleProduct)
class SimpleProductAdmin(admin.ModelAdmin):
    list_display = ['name','link']

@admin.register(Balance)
class BalancesAdmin(admin.ModelAdmin):
    list_display = ['account','balance','updated_datetime']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['balance','processed_datetime','purchase_request','total_value']

@admin.register(DocumentNumber)
class DocumentNumberAdmin(admin.ModelAdmin):
    list_display = ['document','prefix','next_counter','last_number']