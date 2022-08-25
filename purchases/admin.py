from typing import Set
from django.contrib import admin, messages
from django.shortcuts import redirect
from django.db.models import Q
from django.utils.text import slugify

from purchases import tracking

from .models.models_metadata import (
    Accounts, Carrier, Department, DocumentNumber,
    Urgency, Vendor, State, Unit
)
from .models.models_data import (
    Balance, PurchaseRequest, Transaction,
    PurchaseRequestAccounts, SimpleProduct,
    SpendCategory, Requisitioner
)
from .models.models_apis import Tracker, TrackingEvent #, create_events #, update_tracker_fields
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class PurchaseRequestInline(admin.TabularInline):
    model = PurchaseRequest
    extra = 0

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['name', 'website', 'state']
    inlines = [PurchaseRequestInline]

@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ['name', 'abbreviation']

class SimpleProductInline(admin.TabularInline):
    model = SimpleProduct
    extra = 0

class PurchaseRequestAccountsInline(admin.TabularInline):
    model = PurchaseRequestAccounts
    extra = 0

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
        # r.update_transactions()

class TrackerInline(admin.TabularInline):
    model = Tracker
    extra = 0
    exclude = ['events','shipment_id']

@admin.register(PurchaseRequest)
class PurchaseRequestAdmin(admin.ModelAdmin):
    list_display = ['number', 'vendor', 'grand_total', 'status','requisitioner', 'slug']
    list_editable = ['status']
    inlines = [SimpleProductInline,PurchaseRequestAccountsInline,TrackerInline]
    actions = [make_awaiting_approval,save_requests] #,update_trackers]
    search_fields = ['number','vendor__name','requisitioner__user__first_name','requisitioner__user__last_name']
    date_hierarchy = 'created_date'

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

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name']

class RequisitionerInline(admin.StackedInline):
    model = Requisitioner

class UserAdmin(BaseUserAdmin):
    inlines = [RequisitionerInline]

@admin.action(description="Save Selected")
def save_requisitioners(modeladmin, request, queryset):
    for q in queryset:
        q.save()

@admin.register(Requisitioner)
class RequisitionerAdmin(admin.ModelAdmin):
    list_display = ['user_full_name','user_email','department']
    actions = [save_requisitioners]
    inlines = [PurchaseRequestInline]

    def user_full_name(self, obj):
        return obj.user.get_full_name()

    @admin.display(description="Email Address")    
    def user_email(self, obj):
        return obj.user.email

class PurchaseRequestAccountsInline(admin.TabularInline):
    model = PurchaseRequestAccounts
    extra = 0

@admin.register(Accounts)
class AccountsAdmin(admin.ModelAdmin):
    list_display = ['account','account_title','program_workday','grant','gift']
    inlines = [PurchaseRequestAccountsInline]

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

class CarrierHasSlugFilter(admin.SimpleListFilter):
    title = "Has Slug"
    parameter_name = 'has-slug'
    
    def lookups(self, request, model_admin):
        return (
            ('true', 'Yes'),
            ('false', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'true':
            return queryset.filter(Q(slug__isnull = False) | Q(slug=''))
        elif self.value() == 'false':
            return queryset.filter(slug__isnull = True)
        else:
            return queryset


class CarrierListFilterBase(admin.SimpleListFilter):
    title = 'Carrier'
    parameter_name = 'carrier'

    class Meta:
        abstract = True

    def lookups(self, request, model_admin):
        carriers = []
        for carrier in Carrier.objects.filter(tracker__isnull = False).distinct():
            carriers.append((carrier.pk, carrier.name))

        return carriers

class EventCarrierListFilter(CarrierListFilterBase):
    def queryset(self, request, queryset):
        if value := self.value():
            return queryset.filter(tracker__carrier__id = value).distinct()
        else:
            return queryset

class TrackerCarrierListFilter(CarrierListFilterBase):
    def queryset(self, request, queryset):
        if value := self.value():
            return queryset.filter(carrier__id = value).distinct()
        else:
            return queryset

class HasTrackerListFilter(admin.SimpleListFilter):
    title = 'Has Tracker'
    parameter_name = 'has-tracker'


    def lookups(self, request, model_admin):
        return (
            ('yes','Yes'),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(tracker__isnull = False).distinct()

@admin.action(description="Create Slug")
def generate_slug(modeladmin:admin.ModelAdmin, request, queryset):
    for counter, object in enumerate(queryset):
        if not object.slug:
            # pass
            print("Name({}): {}".format(counter, object.name))
            object.slug = slugify(object.name, allow_unicode=True)
            print("Slug({}): {}".format(counter, object.slug))

    # print(modeladmin.model)
    count = modeladmin.model.objects.bulk_update(queryset, ['slug'], batch_size=100)
    messages.success(request, message="{} records successfully updated.".format(count))

@admin.register(Carrier)
class CarrierAdmin(admin.ModelAdmin):
    list_display = ['name','carrier_code','slug']
    inlines = [TrackerInline]
    search_fields = ['name','carrier_code','slug']
    list_filter = (HasTrackerListFilter,CarrierHasSlugFilter)
    actions = [generate_slug]

class TrackingEventInline(admin.TabularInline):
    model = TrackingEvent
    extra = 0

@admin.action(description="Update Tracker(s)")
def update_selected_trackers(modeladmin, request, queryset):
    list = []
    for q in queryset:
        d = (
            q.tracking_number,
            q.carrier.carrier_code
        )
        list.append(d)

    try:
        updated_trackers = tracking.update_tracking_details(list)
    except ValueError as err:
        messages.error(request, "{}".format(err))

    if updated_trackers:
        tracker_objs = []
        event_update_count = 0
        for t in updated_trackers:
            carrier = Carrier.objects.get(carrier_code=t.get('carrier_code'))
            t_obj = Tracker.objects.get(tracking_number=t.get('tracking_number'),carrier=carrier)
            t_obj.status = t.get('status')
            t_obj.sub_status = t.get('sub_status')
            t_obj.delivery_estimate = t.get('delivery_estimate')
            t_obj.events = t.get('events')

            events_hash = t.get('events_hash')

            if t_obj.events_hash != str(events_hash):
                event_update_count += 1
                _,_ = t_obj.create_events(t.get('events'))
                t_obj.events_hash = t.get('events_hash')

            tracker_objs.append(t_obj)

        update_count = Tracker.objects.bulk_update(tracker_objs,['status','sub_status','delivery_estimate','events','events_hash'])

        if update_count == 0:
            messages.add_message(request, messages.WARNING, "No objects found to update!")
        elif update_count == 1:
            messages.add_message(request, messages.SUCCESS, "{0:d} object updated.".format(update_count))
        else:
            messages.add_message(request, messages.SUCCESS, "{0:d} objects updated.".format(update_count))

        messages.add_message(request, messages.SUCCESS, "{0} tracker(s) had updated events.".format(event_update_count))

@admin.action(description="Add missing first event time(s)")
def add_first_event_time(modeladmin, request, queryset):
    objs = []
    for tracker in queryset:
        if not tracker.earliest_event_time and tracker.trackingevent_set.count() > 0:
            objs.append(tracker)
            tracker.earliest_event_time = tracker.trackingevent_set.earliest().time_utc
            messages.success(request, "Tracker {} updated with {} as earliest time.".format(tracker, tracker.earliest_event_time))

    Tracker.objects.bulk_update(objs, ['earliest_event_time'])

@admin.register(Tracker)
class TrackerAdmin(admin.ModelAdmin):
    list_display = ['id','status','sub_status','carrier','purchase_request']
    inlines = [TrackingEventInline]
    actions = [update_selected_trackers, add_first_event_time]
    list_filter = [TrackerCarrierListFilter]

    def response_change(self, request, obj, post_url_continue = ...):
        url = redirect('tracker_detail', pk=obj.pk)

        # url = super().response_change(request, obj)
        
        return url

    def response_delete(self, request, obj, post_url_continue = ...):
        url = redirect('tracker_list')

        return url

@admin.register(TrackingEvent)
class TrackingEventAdmin(admin.ModelAdmin):
    list_display = ['tracker','description']
    search_fields = ['tracker__carrier__name']
    date_hierarchy = 'time_utc'
    list_filter = [EventCarrierListFilter]

@admin.register(SimpleProduct)
class SimpleProductAdmin(admin.ModelAdmin):
    list_display = ['name','link','identifier','purchase_request']
    search_fields = [
        'purchase_request',
        'purchase_request__requisitioner__user__first_name',
        'purchase_request__requisitioner__user__last_name',
        'purchase_request__vendor__name'
    ]

@admin.register(Balance)
class BalancesAdmin(admin.ModelAdmin):
    list_display = ['account','balance','updated_datetime']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['balance','processed_datetime','purchase_request','total_value']

@admin.register(DocumentNumber)
class DocumentNumberAdmin(admin.ModelAdmin):
    list_display = ['document','prefix','next_counter','last_number']
    list_editable = ['next_counter']