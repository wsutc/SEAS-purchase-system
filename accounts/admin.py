from django.contrib import admin
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _

from .models import (
    Account,
    AccountGroup,
    BalanceAdjustment,
    BaseTransaction,
    SpendCategory,
    Transaction,
)


# Register your models here.
class TransactionInline(admin.TabularInline):
    model = BaseTransaction
    extra = 0


# class AccountGroupInline(admin.StackedInline):
#     model = AccountGroup
#     extra = 0


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


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ["name", "account", "fund_type", "fund", "current_balance"]
    search_fields = ["name", "account", "fund"]
    list_filter = ["fund_type", "in_use", AccountGroupsListFilter]
    inlines = [TransactionInline]

    actions = ["recalculate_balance"]

    @admin.action(description="Recalculate Balance(s)")
    def recalculate_balance(self, request, queryset):
        for q in queryset:
            q.current_balance = q.calculate_aggregate()

            # q.save()

        count = queryset.bulk_update(queryset, ["current_balance"])

        self.message_user(request, f"{count} item(s) updated")

    def response_change(self, request, obj, post_url_continue=...):
        url = redirect(obj)

        return url

    def save_model(self, request, obj, form, change) -> None:
        if change and "starting_balance" in form.changed_data:
            obj.current_balance = obj.calculate_aggregate()
        return super().save_model(request, obj, form, change)


@admin.register(AccountGroup)
class AccountGroupAdmin(admin.ModelAdmin):
    list_display = ["name", "account_count"]
    search_fields = ["name", "accounts"]
    filter_horizontal = ["accounts"]

    def account_count(self, obj):

        count = obj.accounts.count()
        return count


@admin.register(BalanceAdjustment)
class BalanceAdjustmentAdmin(admin.ModelAdmin):
    list_display = ["account", "amount", "reason", "date_time"]
    search_fields = ["account", "reason", "date_time"]
    list_filter = ["account"]
    date_hierarchy = "date_time"


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ["account", "amount", "date_time", "purchase_request"]
    list_filter = ["account"]


@admin.register(SpendCategory)
class SpendCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]
