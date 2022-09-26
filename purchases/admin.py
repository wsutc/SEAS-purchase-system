# from typing import Set

from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Q
from django.shortcuts import redirect
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from purchases.tracking import update_tracking_details

from .models import (  # Transaction,
    AccountGroup,
    Accounts,
    Balance,
    Carrier,
    Department,
    DocumentNumber,
    PurchaseRequest,
    PurchaseRequestAccount,
    Requisitioner,
    SimpleProduct,
    SpendCategory,
    State,
    Status,
    Tracker,
    TrackingEvent,
    Unit,
    Urgency,
    Vendor,
    VendorOrder,
)


class PurchaseRequestInline(admin.TabularInline):
    model = PurchaseRequest
    extra = 0


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ["name", "website", "state"]
    inlines = [PurchaseRequestInline]


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ["name", "abbreviation"]


class SimpleProductInline(admin.TabularInline):
    model = SimpleProduct
    extra = 0


class PurchaseRequestAccountInline(admin.TabularInline):
    model = PurchaseRequestAccount
    extra = 0


@admin.action(description="Change Selected to 'Awaiting Approval'")
def make_awaiting_approval(modeladmin, request, queryset):
    queryset.update(status="1")


@admin.action(description="Change Selected to 'Approved'")
def make_approved(modeladmin, request, queryset):
    queryset.update(status="2")


@admin.action(description="Change Selected to 'Ordered'")
def make_ordered(modeladmin, request, queryset):
    queryset.update(status="6")


@admin.action(description="Update Totals")
def save_requests(modeladmin, request, queryset):
    for r in queryset:
        r.update_totals()
        # r.update_transactions()


class TrackerInline(admin.TabularInline):
    model = Tracker
    extra = 0
    exclude = ["events", "shipment_id"]


# @admin.register(TrackerItem)
# class TrackerItemAdmin(admin.ModelAdmin):
#     list_display = [
#         "simple_product",
#         "purchase_request",
#         "tracker",
#         "shipment_received",
#     ]
#     list_filter = [
#         ("simple_product__purchase_request", admin.RelatedOnlyFieldListFilter),
#     ]
#     search_fields = ["simple_product", "tracker"]

#     def purchase_request(self, obj):
#         value = obj.simple_product.purchase_request
#         return value

#     # @property
#     # def vendor(self, obj):
#     #     value = obj.tracker.vendor
#     #     return value


# class TrackerItemInline(admin.TabularInline):
#     model = TrackerItem


@admin.register(PurchaseRequest)
class PurchaseRequestAdmin(admin.ModelAdmin):
    list_display = [
        "number",
        "vendor",
        "grand_total",
        "status",
        "requisitioner",
        "slug",
    ]
    list_editable = ["status"]
    inlines = [SimpleProductInline, PurchaseRequestAccountInline]
    actions = [make_awaiting_approval, save_requests]  # ,update_trackers]
    search_fields = [
        "number",
        "vendor__name",
        "requisitioner__user__first_name",
        "requisitioner__user__last_name",
    ]
    date_hierarchy = "created_date"
    list_filter = ["status", "requisitioner", "vendor"]

    @admin.display(description="Tracking Status")
    def get_tracker_status(self, obj):
        if obj.tracker:
            return obj.tracker.status
        return

    @admin.display(description="Update Tracker(s)")
    def update_tracker(self, obj):
        if obj.tracker:
            update_tracking_details(obj.tracker)
            return obj.tracker.status
        return

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.update_totals()


@admin.register(VendorOrder)
class VendorOrderAdmin(admin.ModelAdmin):
    list_display = ["name", "grand_total", "link"]
    list_filter = [
        ("purchase_requests", admin.RelatedOnlyFieldListFilter),
        ("vendor", admin.RelatedOnlyFieldListFilter),
        "purchase_requests__requisitioner",
        "purchase_requests__status",
    ]
    search_fields = ["purchase_requests", "vendor"]

    def response_change(self, request, obj, post_url_continue=...):

        return redirect_object_or_next(obj, request)

    def response_delete(self, request, obj, post_url_continue=...):

        return redirect_object_or_next(obj, request)


def redirect_object_or_next(object, request, next_param="next"):
    """Redirect to specified 'next' page or object's detail page.

    :param object: Object/model to be redirected to if no 'next' page specified
    :type object: Django models.Model object
    :param request: The request as specified by the server
    :type request: HTTPRequest
    :param next_param: Paramater used in URL to specify 'next' page
    :type next_param: str, optional
    """
    next = request.GET.get(next_param, None)
    if next:
        url = next
    else:
        url = object

    return redirect(url)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ["name"]


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
    list_display = ["user_full_name", "user_email", "department"]
    actions = [save_requisitioners]
    inlines = [PurchaseRequestInline]

    def user_full_name(self, obj):
        return obj.user.get_full_name()

    @admin.display(description="Email Address")
    def user_email(self, obj):
        return obj.user.email


# class PurchaseRequestAccountInline(admin.TabularInline):
#     model = PurchaseRequestAccount
#     extra = 0


@admin.register(AccountGroup)
class AccountGroupAdmin(admin.ModelAdmin):
    list_display = ["name", "account_count"]
    filter_horizontal = [
        "accounts",
    ]

    def account_count(self, obj):

        count = obj.accounts.count()
        return count


class AccountGroupsListFilter(admin.SimpleListFilter):
    title = _("groups")
    parameter_name = "accountgroup"

    def lookups(self, request, model_admin):
        qs = AccountGroup.objects.values_list("slug", "name")
        return qs

    def queryset(self, request, queryset):
        if value := self.value():
            queryset = queryset.filter(accountgroup__slug=value)

        return queryset


class HasSlugFilter(admin.SimpleListFilter):
    title = "Has Slug"
    parameter_name = "has-slug"

    def lookups(self, request, model_admin):
        return (
            ("true", "Yes"),
            ("false", "No"),
        )

    def queryset(self, request, queryset):
        if self.value() == "true":
            return queryset.filter(Q(slug__isnull=False) | Q(slug=""))
        elif self.value() == "false":
            return queryset.filter(slug__isnull=True)
        else:
            return queryset


@admin.register(Accounts)
class AccountsAdmin(admin.ModelAdmin):
    list_display = ["account", "account_title", "program_workday", "grant", "gift"]
    # inlines = [PurchaseRequestAccountInline]
    search_fields = ["account", "account_title", "program_workday", "grant", "gift"]
    list_filter = [
        # "program_workday__is_null",
        AccountGroupsListFilter,
        HasSlugFilter,
        # ("grant__is_null", admin.BooleanFieldListFilter),
        # ("gift_is_null", admin.BooleanFieldListFilter),
    ]


@admin.register(SpendCategory)
class SpendCategoryAdmin(admin.ModelAdmin):
    list_display = ["code", "description", "object", "subobject"]


@admin.register(PurchaseRequestAccount)
class PurchaseRequestAccountAdmin(admin.ModelAdmin):
    list_display = ["account", "purchase_request"]


@admin.register(Unit)
class UnitsAdmin(admin.ModelAdmin):
    list_display = ["unit", "abbreviation"]


@admin.register(Urgency)
class UrgencyAdmin(admin.ModelAdmin):
    list_display = ["name", "note"]


class CarrierHasSlugFilter(admin.SimpleListFilter):
    title = "Has Slug"
    parameter_name = "has-slug"

    def lookups(self, request, model_admin):
        return (
            ("true", "Yes"),
            ("false", "No"),
        )

    def queryset(self, request, queryset):
        if self.value() == "true":
            return queryset.filter(Q(slug__isnull=False) | Q(slug=""))
        elif self.value() == "false":
            return queryset.filter(slug__isnull=True)
        else:
            return queryset


class CarrierListFilterBase(admin.SimpleListFilter):
    title = "Carrier"
    parameter_name = "carrier"

    class Meta:
        abstract = True

    def lookups(self, request, model_admin):
        carriers = []
        for carrier in Carrier.objects.filter(tracker__isnull=False).distinct():
            carriers.append((carrier.pk, carrier.name))

        return carriers


class EventCarrierListFilter(CarrierListFilterBase):
    def queryset(self, request, queryset):
        if value := self.value():
            return queryset.filter(tracker__carrier__id=value).distinct()
        else:
            return queryset


class TrackerCarrierListFilter(CarrierListFilterBase):
    def queryset(self, request, queryset):
        if value := self.value():
            return queryset.filter(carrier__id=value).distinct()
        else:
            return queryset


class HasTrackerListFilter(admin.SimpleListFilter):
    title = "Has Tracker"
    parameter_name = "has-tracker"

    def lookups(self, request, model_admin):
        return (("yes", "Yes"),)

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(tracker__isnull=False).distinct()


@admin.action(description="Create Slug")
def generate_slug(modeladmin: admin.ModelAdmin, request, queryset):
    for counter, object in enumerate(queryset):
        if not object.slug:
            # pass
            print(f"Name({counter}): {object.name}")
            object.slug = slugify(object.name, allow_unicode=True)
            print(f"Slug({counter}): {object.slug}")

    # print(modeladmin.model)
    count = modeladmin.model.objects.bulk_update(queryset, ["slug"], batch_size=100)
    messages.success(request, message=f"{count} records successfully updated.")


@admin.register(Carrier)
class CarrierAdmin(admin.ModelAdmin):
    list_display = ["name", "carrier_code", "slug"]
    inlines = [TrackerInline]
    search_fields = ["name", "carrier_code", "slug"]
    list_filter = (HasTrackerListFilter, CarrierHasSlugFilter)
    actions = [generate_slug]


@admin.action(description="Move Up 1")
def move_up_one(modeladmin: admin.ModelAdmin, request, queryset):
    if queryset.count() != 1:
        # messages.error(request, message="Exactly one item can be chose for reordering; {} chosen.".format(count))
        modeladmin.message_user(
            request,
            message="Exactly one item can be chose for reordering; {} chosen.".format(
                queryset.count()
            ),
        )
        return

    obj = queryset[0]
    obj_rank = obj.rank
    try:
        queryset.model.objects.move(obj, obj_rank - 1)
    except ValueError as err:
        modeladmin.message_user(request, message=err, level="warning")


@admin.action(description="Move Down 1")
def move_down_one(modeladmin: admin.ModelAdmin, request, queryset):
    if queryset.count() != 1:
        # messages.error(request, message="Exactly one item can be chose for reordering; {} chosen.".format(count))
        modeladmin.message_user(
            request,
            message="Exactly one item can be chose for reordering; {} chosen.".format(
                queryset.count()
            ),
        )
        return

    obj = queryset[0]
    obj_rank = obj.rank
    try:
        queryset.model.objects.move(obj, obj_rank + 1)
    except ValueError as err:
        modeladmin.message_user(request, message=err, level="warning")


@admin.action(description="Move to Top")
def move_to_top(modeladmin, request, queryset):
    if queryset.count() != 1:
        modeladmin.message_user(
            request,
            message="Exactly one item can be chose for reordering; {} chosen.".format(
                queryset.count()
            ),
        )
        return

    obj = queryset[0]
    try:
        queryset.model.objects.move_to_top(obj)
    except ValueError as err:
        modeladmin.message_user(request, message=err, level="warning")


@admin.action(description="Move to End")
def move_to_end(modeladmin, request, queryset):
    if queryset.count() != 1:
        modeladmin.message_user(
            request,
            message="Exactly one item can be chose for reordering; {} chosen.".format(
                queryset.count()
            ),
        )
        return

    obj = queryset[0]
    try:
        queryset.model.objects.move_to_end(obj)
    except ValueError as err:
        modeladmin.message_user(request, message=err, level="warning")


@admin.action(description="Normalize")
def normalize(modeladmin, request, queryset):
    queryset.model.objects.normalize_ranks("parent_model")


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ["name", "parent_model", "rank", "open"]
    list_filter = ["parent_model"]
    actions = [move_to_top, move_up_one, move_down_one, move_to_end, normalize]
    list_editable = ["open"]


class TrackingEventInline(admin.TabularInline):
    model = TrackingEvent
    extra = 0


@admin.action(description="Update Tracker(s)")
def update_selected_trackers(modeladmin, request, queryset):
    list = []
    for q in queryset:
        d = (q.tracking_number, q.carrier.carrier_code)
        list.append(d)

    try:
        updated_trackers = update_tracking_details(list)
    except ValueError as err:
        messages.error(request, f"{err}")

    if updated_trackers:
        tracker_objs = []
        event_update_count = 0
        for t in updated_trackers:
            carrier = Carrier.objects.get(carrier_code=t.get("carrier_code"))
            t_obj = Tracker.objects.get(
                tracking_number=t.get("tracking_number"), carrier=carrier
            )
            t_obj.status = t.get("status")
            t_obj.sub_status = t.get("sub_status")
            t_obj.delivery_estimate = t.get("delivery_estimate")
            t_obj.events = t.get("events")

            events_hash = t.get("events_hash")

            if t_obj.events_hash != str(events_hash):
                event_update_count += 1
                _, _ = t_obj.create_events(t.get("events"))
                t_obj.events_hash = t.get("events_hash")

            tracker_objs.append(t_obj)

        update_count = Tracker.objects.bulk_update(
            tracker_objs,
            ["status", "sub_status", "delivery_estimate", "events", "events_hash"],
        )

        if update_count == 0:
            messages.add_message(
                request, messages.WARNING, "No objects found to update!"
            )
        elif update_count == 1:
            messages.add_message(
                request, messages.SUCCESS, f"{update_count:d} object updated."
            )
        else:
            messages.add_message(
                request, messages.SUCCESS, f"{update_count:d} objects updated."
            )

        messages.add_message(
            request,
            messages.SUCCESS,
            f"{event_update_count} tracker(s) had updated events.",
        )


@admin.action(description="Add missing first event time(s)")
def add_first_event_time(modeladmin, request, queryset):
    objs = []
    for tracker in queryset:
        if not tracker.earliest_event_time and tracker.trackingevent_set.count() > 0:
            objs.append(tracker)
            tracker.earliest_event_time = tracker.trackingevent_set.earliest().time_utc
            messages.success(
                request,
                "Tracker {} updated with {} as earliest time.".format(
                    tracker, tracker.earliest_event_time
                ),
            )

    Tracker.objects.bulk_update(objs, ["earliest_event_time"])


@admin.register(Tracker)
class TrackerAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "sub_status", "carrier", "earliest_event_time"]
    inlines = [TrackingEventInline]
    actions = [update_selected_trackers, add_first_event_time]
    list_filter = [TrackerCarrierListFilter, "status"]
    search_fields = ["id", "sub_status"]

    def response_change(self, request, obj, post_url_continue=...):
        url = redirect(obj)

        # url = super().response_change(request, obj)

        return url

    def response_delete(self, request, obj, post_url_continue=...):
        url = redirect("tracker_list")

        return url


@admin.register(TrackingEvent)
class TrackingEventAdmin(admin.ModelAdmin):
    list_display = ["tracker", "description"]
    search_fields = ["tracker__carrier__name"]
    date_hierarchy = "time_utc"
    list_filter = [EventCarrierListFilter]


@admin.register(SimpleProduct)
class SimpleProductAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "link",
        "identifier",
        "purchase_request",
        "quantity",
        "unit_price",
        "rank",
    ]
    list_editable = ["unit_price", "quantity"]
    list_filter = ["purchase_request"]
    search_fields = [
        "identifier",
        # "purchase_request",
        # "purchase_request__requisitioner__user__first_name",
        # "purchase_request__requisitioner__user__last_name",
        # "purchase_request__vendor__name",
    ]
    # inlines = [TrackerItemInline]


@admin.register(Balance)
class BalancesAdmin(admin.ModelAdmin):
    list_display = ["account", "balance", "updated_datetime"]


# @admin.register(Transaction)
# class TransactionAdmin(admin.ModelAdmin):
#     list_display = ["balance", "processed_datetime", "purchase_request", "total_value"]


@admin.register(DocumentNumber)
class DocumentNumberAdmin(admin.ModelAdmin):
    list_display = ["document", "prefix", "next_counter", "last_number"]
    list_editable = ["next_counter"]
