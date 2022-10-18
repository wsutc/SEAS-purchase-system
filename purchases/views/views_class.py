import datetime
import logging
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin

# from django.contrib.auth.models import User
from django.db.models import ExpressionWrapper, F, OuterRef, Subquery, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from django.views.generic.detail import SingleObjectMixin
from django_listview_filters.filters import (  # AllValuesFieldListFilter,
    ChoicesFieldListViewFilter,
    RelatedFieldListViewFilter,
)
from djmoney.models.fields import MoneyField

from globals.models import DefaultValue
from purchases.forms import (
    AddVendorForm,
    AddVendorOrderForm,
    CreateUserForm,
    CustomPurchaseRequestForm,
    NewPRForm,
    PurchaseRequestAccountFormset,
    SimpleProductCopyForm,
    SimpleProductFormset,
    TrackerForm,
)
from purchases.models import (  # Transaction,
    Accounts,
    Balance,
    PurchaseRequest,
    Requisitioner,
    SimpleProduct,
    Status,
    Tracker,
    Vendor,
    VendorOrder,
    requisitioner_from_user,
)
from purchases.models.models_metadata import PurchaseRequestAccount
from web_project.helpers import (  # truncate_string,
    PaginatedListMixin,
    max_decimal_places,
    redirect_to_next,
)

# from typing import Any, Dict

logger = logging.getLogger(__name__)


class VendorListView(PaginatedListMixin, ListView):
    context_object_name = "vendors"
    queryset = Vendor.objects.order_by("name")


class SimpleView(SingleObjectMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["purchase_request_statuses"] = Status.objects.filter(
            parent_model="PR"
        ).order_by("rank")

        return context


class VendorOrderCreateView(CreateView):
    form_class = AddVendorOrderForm
    template_name = "purchases/vendororder_create.html"

    def form_valid(self, form):
        if hasattr(form, "message"):
            messages.info(self.request, form.message)

        return super().form_valid(form)


class VendorOrderDetailView(SimpleView, DetailView):
    model = VendorOrder
    query_pk_and_slug = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        trackers = []
        object = self.get_object()

        prs = object.purchase_requests.all()

        for request in prs:
            for tracker in request.tracker_set.all():
                trackers.append(tracker)

        context["trackers"] = trackers

        return context


class VendorOrderListView(PaginatedListMixin, ListView):
    context_object_name = "vendororder"
    queryset = VendorOrder.objects.all()
    list_filter = [
        ("purchase_requests", RelatedFieldListViewFilter),
        ("vendor", RelatedFieldListViewFilter),
        ("purchase_requests__requisitioner", RelatedFieldListViewFilter),
        ("purchase_requests__status", ChoicesFieldListViewFilter),
        # ("o.purchase_requests.last.tracker_set.last.status"),
    ]

    def get_queryset(self):
        qs = super().get_queryset()

        # add total of PR grand totals as new field `calculated_total`
        prs = (
            PurchaseRequest.objects.filter(pk__in=OuterRef("purchase_requests"))
            .order_by()
            .values("pk")
        )
        calculated_total = prs.annotate(calc_total=Sum("grand_total")).values(
            "calc_total"
        )

        qs = qs.annotate(calculated_total=Subquery(calculated_total),).annotate(
            difference=ExpressionWrapper(
                F("calculated_total")
                - (F("subtotal") + F("shipping") + F("sales_tax")),
                output_field=MoneyField(),
            )
        )

        return qs


class VendorOrderCurrentListView(VendorOrderListView):
    template_name = "purchases/vendororder_current_list.html"
    queryset = VendorOrder.objects.filter(purchase_requests__status__open=True)


class SimpleProductListView(PaginatedListMixin, ListView):
    context_object_name = "simpleproduct"
    queryset = SimpleProduct.objects.order_by("purchase_request__vendor", "name")
    list_filter = [
        ("purchase_request__vendor", RelatedFieldListViewFilter),
        ("purchase_request__requisitioner", RelatedFieldListViewFilter),
        ("purchase_request__status", ChoicesFieldListViewFilter),
        ("purchase_request", RelatedFieldListViewFilter),
        # ("purchase_request__tracker_set__latest__status", AllValuesFieldListFilter),
    ]

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        # TODO: make this more elegant
        # sort vendor as lower case (python sorts lower different than upper by default)
        filter_name = "purchase_request__vendor"

        # django-listview-filters added `get_filter_by_name` in later versions
        # (should be removed)
        try:
            filter = self.get_filter_by_name(filter_name)
        except Exception:
            if len(self.filter_specs) > 0:
                for filter_spec in self.filter_specs:
                    filter = (
                        filter_spec if filter_spec.field_path == filter_name else None
                    )
            else:
                filter = None

        if filter:
            filter.lookup_choices = sorted(
                filter.lookup_choices, key=lambda x: x[1].lower()
            )

            if settings.DEBUG:
                for counter, choice in enumerate(filter.lookup_choices):
                    logger.debug(f"Choice {counter}: {choice}")

        # add context for max digits of unit price field for formatting
        qs = context["object_list"]

        unitprice_values = qs.values_list("unit_price", flat=True)

        context["unitprice_maxdigits"] = max_decimal_places(unitprice_values)

        return context


class SimpleProductPRListView(SimpleProductListView):
    list_filter = []

    def get_queryset(self):
        qs = super().get_queryset()
        slug = self.kwargs["purchaserequest"]
        purchase_request = PurchaseRequest.objects.filter(slug=slug)
        qs = qs.filter(purchase_request__in=purchase_request)

        logger.info(f"Purchase Request: {purchase_request.first()}")

        return qs


class PurchaseRequestListViewBase(PaginatedListMixin, ListView):
    context_object_name = "purchaserequests"
    queryset = PurchaseRequest.objects.order_by("-created_date")
    list_filter = [
        ("status", RelatedFieldListViewFilter),
        ("vendor", RelatedFieldListViewFilter),
        ("requisitioner", RelatedFieldListViewFilter),
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["purchase_request_statuses"] = Status.objects.filter(
            parent_model="PR"
        ).order_by("rank")
        return context

    class Meta:
        abstract = True


class PurchaseRequestListView(PurchaseRequestListViewBase):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["show_link"] = (_("show open"), "open_pr")

        return context


class RequisitionerPurchaseRequestListView(PurchaseRequestListViewBase):
    list_filter = [
        ("status", ChoicesFieldListViewFilter),
        ("vendor", RelatedFieldListViewFilter),
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["show_link"] = (_("show open"), "open_pr")

        return context

    def get_queryset(self):
        self.requisitioner = get_object_or_404(
            Requisitioner, slug=self.kwargs["requisitioner"]
        )
        qs = PurchaseRequest.objects.filter(requisitioner=self.requisitioner).order_by(
            "-created_date"
        )

        qs = self.filter_queryset(qs)

        return qs


class OpenPurchaseRequestListView(PurchaseRequestListViewBase):
    # pr = PurchaseRequest.PurchaseRequestStatuses
    # current_statuses = [pr.WL, pr.AP, pr.OR, pr.PT, pr.SH, pr.AA]
    queryset = PurchaseRequest.objects.filter(status__open=True).order_by(
        "-created_date"
    )
    list_filter = [
        ("vendor", RelatedFieldListViewFilter),
        ("requisitioner", RelatedFieldListViewFilter),
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["show_link"] = (_("show all"), "home")

        return context


class VendorDetailView(DetailView):
    model = Vendor
    query_pk_and_slug = True


def get_status_choices(model: Status.StatusModel):
    statuses = PurchaseRequest.PurchaseRequestStatuses
    status_choices = statuses.values

    def dict_f(input):
        output = f'"name": {statuses(input).name}, "label": {statuses(input).label}'
        return output

    # dict_f = lambda x: {"name": statuses(x).name, "label": statuses(x).label}

    return [dict_f(x) for x in status_choices]


class PurchaseRequestDetailView(SimpleView, DetailView):
    model = PurchaseRequest
    template_name = "purchases/purchaserequest_detail.html"
    context_object_name = "purchaserequest"
    query_pk_and_slug = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add context for max digits of unit price field for formatting
        unitprice_values = self.object.simpleproduct_set.values_list(
            "unit_price", flat=True
        )

        context["simpleproducts_unitprice_maxdigits"] = max_decimal_places(
            unitprice_values
        )

        # add context for fund type column
        budgets = []
        for budget in self.object.purchaserequestaccount_set.all():
            match budget.account.fund_type:
                case "PG":
                    funds = [budget.account, "", ""]
                case "GF":
                    funds = ["", budget.account, ""]
                case "GR":
                    funds = ["", "", budget.account]
            budget_dict = {
                "funds_list": funds,
                "spend_category": budget.spend_category_ext,
                "distribution_type": budget.distribution_type,
                "distribution": budget.distribution_input,
            }
            budgets.append(budget_dict)

        context["budgets"] = budgets

        dist_types = {
            "percent": PurchaseRequestAccount.DistributionType.PERCENT,
            "amount": PurchaseRequestAccount.DistributionType.AMOUNT,
        }

        context["distribution_types"] = dist_types

        # context["sales_tax_perc"] = self.object.sales_tax_perc * self.object.subtotal

        return context


class RequisitionerCreateView(CreateView):
    form_class = CreateUserForm
    template_name = "purchases/requisitioner_create.html"

    def form_valid(self, form):
        user = form.save()
        user.refresh_from_db()

        user.requisitioner.wsu_id = form.cleaned_data.get("wsu_id")
        user.save()

        return redirect(user.requisitioner)


class RequisitionerDetailView(DetailView):
    model = Requisitioner
    template_name = "purchases/requisitioner_detail.html"
    query_pk_and_slug = True


class RequisitionerListView(PaginatedListMixin, ListView):
    context_object_name = "requisitioners"
    # admin_user = User.objects.filter(username="admin").first()
    queryset = Requisitioner.objects.exclude(user__username="admin").order_by("user")


class RequisitionerUpdateView(UpdateView):
    model = Requisitioner
    form_class = CreateUserForm
    template_name = "purchases/requisitioner_create.html"
    query_pk_and_slug = True


class VendorDeleteView(DeleteView):
    model = Vendor
    success_url = reverse_lazy("all_vendors")

    def form_valid(self, *args, **kwargs):
        object = self.get_object()
        object.delete()

        redirect_url = redirect_to_next(self.request, "all_vendors")

        return redirect(redirect_url)


class VendorCreateView(CreateView):
    form_class = AddVendorForm
    template_name = "purchases/add_vendor.html"


# class VendorModalCreateView(BSModalCreateView):
#     template_name = 'purchases/vendor_create_modal.html'
#     form_class = VendorModelForm
#     success_message = 'Success: New Vendor created.'


class PurchaseRequestCreateView(PermissionRequiredMixin, CreateView):
    permission_required = "purchases.add_purchaserequest"
    form_class = NewPRForm
    template_name = "purchases/new_pr.html"

    def get_initial(self):
        req_obj = requisitioner_from_user(self.request.user)
        sales_tax_rate = DefaultValue.objects.get_value("salestaxrate")
        instruction = DefaultValue.objects.get_value("purchaserequestinstructions")
        day_offset = DefaultValue.objects.get_value("needbyoffset", default=21)
        date_today = datetime.datetime.today()
        day_delta = datetime.timedelta(days=int(day_offset))
        need_by_date = date_today + day_delta
        self.initial.update(
            {
                "requisitioner": req_obj,
                "sales_tax_rate": Decimal(sales_tax_rate),
                "instruction": instruction,
                "need_by_date": need_by_date,
            }
        )

        initial_values = super().get_initial()
        return initial_values

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["purchase_request_items_formset"] = SimpleProductFormset(prefix="items")
        context["purchase_request_accounts_formset"] = PurchaseRequestAccountFormset(
            prefix="accounts"
        )
        # context['requisitioner'] = Requisitioner.objects.get(user=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        purchase_request_items_formset = SimpleProductFormset(
            self.request.POST, prefix="items"
        )
        purchase_request_accounts_formset = PurchaseRequestAccountFormset(
            self.request.POST, prefix="accounts"
        )
        if not (priValid := purchase_request_items_formset.is_valid()):
            print(purchase_request_items_formset.errors)
        if not (praValid := purchase_request_accounts_formset.is_valid()):
            print(purchase_request_accounts_formset.errors)
        if form.is_valid() and priValid and praValid:
            return self.form_valid(
                form, purchase_request_items_formset, purchase_request_accounts_formset
            )
        else:
            return self.form_invalid(
                form, purchase_request_items_formset, purchase_request_accounts_formset
            )

    def form_valid(
        self, form, purchase_request_items_formset, purchase_request_accounts_formset
    ):
        self.object = form.save(commit=False)
        self.object.save()

        # Add Items
        purchase_request_items = purchase_request_items_formset.save(commit=False)
        for item in purchase_request_items:
            item.purchase_request = self.object
            item.save()

        # Add Accounts
        purchase_request_accounts = purchase_request_accounts_formset.save(commit=False)
        for account in purchase_request_accounts:
            account.purchase_request = self.object
            account.save()

        # Set PR totals and update balance (balance isn't functional)
        self.object.update_totals()

        return redirect(self.object)

    def form_invalid(
        self, form, purchase_request_items_formset, purchase_request_accounts_formset
    ):
        return self.render_to_response(
            self.get_context_data(
                form=form,
                purchase_request_items_formset=purchase_request_items_formset,
                purchase_request_accounts_formset=purchase_request_accounts_formset,
            )
        )


class CustomPurchaseRequestCreateView(PermissionRequiredMixin, CreateView):
    permission_required = "purchases.add_purchaserequest"
    form_class = CustomPurchaseRequestForm
    template_name = "purchases/new_pr.html"

    def get_initial(self):
        req_obj = requisitioner_from_user(self.request.user)
        self.initial.update({"requisitioner": req_obj})
        return super().get_initial()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["purchase_request_items_formset"] = SimpleProductFormset(prefix="items")
        context["purchase_request_accounts_formset"] = PurchaseRequestAccountFormset(
            prefix="accounts"
        )
        # context['requisitioner'] = Requisitioner.objects.get(user=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        purchase_request_items_formset = SimpleProductFormset(
            self.request.POST, prefix="items"
        )
        purchase_request_accounts_formset = PurchaseRequestAccountFormset(
            self.request.POST, prefix="accounts"
        )
        if not (priValid := purchase_request_items_formset.is_valid()):
            print(purchase_request_items_formset.errors)
        if not (praValid := purchase_request_accounts_formset.is_valid()):
            print(purchase_request_accounts_formset.errors)
        if form.is_valid() and priValid and praValid:
            return self.form_valid(
                form, purchase_request_items_formset, purchase_request_accounts_formset
            )
        else:
            return self.form_invalid(
                form, purchase_request_items_formset, purchase_request_accounts_formset
            )

    def form_valid(
        self, form, purchase_request_items_formset, purchase_request_accounts_formset
    ):
        self.object = form.save(commit=False)
        self.object.save()

        # Add Items
        purchase_request_items = purchase_request_items_formset.save(commit=False)
        for item in purchase_request_items:
            item.purchase_request = self.object
            item.save()

        # Add Accounts
        purchase_request_accounts = purchase_request_accounts_formset.save(commit=False)
        for account in purchase_request_accounts:
            account.purchase_request = self.object
            account.save()

        # Set PR totals and update balance (balance isn't functional)
        self.object.update_totals()

        return redirect(self.object)

    def form_invalid(
        self, form, purchase_request_items_formset, purchase_request_accounts_formset
    ):
        return self.render_to_response(
            self.get_context_data(
                form=form,
                purchase_request_items_formset=purchase_request_items_formset,
                purchase_request_accounts_formset=purchase_request_accounts_formset,
            )
        )


class PurchaseRequestUpdateView(UpdateView):
    permission_required = "purchases.change_purchaserequest"
    model = PurchaseRequest
    form_class = NewPRForm
    template_name = "purchases/purchaserequest_update.html"
    query_pk_and_slug = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["purchase_request_items_formset"] = SimpleProductFormset(
                self.request.POST, instance=self.object, prefix="items"
            )
            context[
                "purchase_request_accounts_formset"
            ] = PurchaseRequestAccountFormset(
                self.request.POST, instance=self.object, prefix="accounts"
            )
        else:
            context["purchase_request_items_formset"] = SimpleProductFormset(
                instance=self.object, prefix="items"
            )
            context[
                "purchase_request_accounts_formset"
            ] = PurchaseRequestAccountFormset(instance=self.object, prefix="accounts")
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        self.object = form.save(commit=False)

        purchase_request_items_formset = context["purchase_request_items_formset"]
        purchase_request_accounts_formset = context["purchase_request_accounts_formset"]

        if not purchase_request_items_formset.is_valid():
            return self.form_invalid(form)
        if not purchase_request_accounts_formset.is_valid():
            return self.form_invalid(form)

        purchase_request_items_formset.save(commit=True)
        purchase_request_accounts_formset.save(commit=True)

        # self.object.save()

        # self.object.update_totals() # this is duplicating work, right?

        # return redirect(self.object)

        return super().form_valid(form)

    def form_invalid(self, form):
        context = self.get_context_data()
        return self.render_to_response(
            self.get_context_data(
                form=form,
                purchase_request_items_formset=context[
                    "purchase_request_items_formset"
                ],
                purchase_request_accounts_formset=context[
                    "purchase_request_accounts_formset"
                ],
            )
        )


class AccountDetailView(SimpleView, DetailView):
    model = Accounts
    template_name = "purchases/account_detail_simple.html"


class PurchaseRequestDeleteView(DeleteView):
    model = PurchaseRequest

    def form_valid(self, *args, **kwargs):
        object = self.get_object()

        messages.success(self.request, f"{object.number} successfully deleted.")

        object.delete()

        redirect_url = redirect_to_next(self.request, "home")

        return redirect(redirect_url)


class VendorUpdateView(UpdateView):
    model = Vendor
    form_class = AddVendorForm
    template_name = "purchases/vendor_update.html"
    query_pk_and_slug = True


class SimpleProductCopyView(UpdateView):
    model = SimpleProduct
    form_class = SimpleProductCopyForm
    template_name = "purchases/simpleproduct_copy.html"

    def form_valid(self, form) -> HttpResponse:
        object = self.get_object()

        object.purchase_request = form.cleaned_data.get("purchase_request")
        object.quantity = form.cleaned_data.get("quantity")
        object.unit_price = form.cleaned_data.get("unit_price")
        object.name = form.cleaned_data.get("name")

        object.pk = None
        object._state.adding = True
        object.save()
        object.purchase_request.update_totals()

        return redirect(object.purchase_request)


class BalancesListView(ListView):
    model = Balance
    template_name = "purchases/balances_list.html"


class BalancesDetailView(DetailView):
    model = Balance
    template_name = "purchases/balances_detail.html"


# class LedgersUpdateView(UpdateView):
#     model = Transaction
#     form_class = LedgersForm
#     template_name = 'purchases/ledgers_create.html'
#     success_url = reverse_lazy('balances_list')

#     # def post(self):
#     #     pass


# class LedgersDetailView(DetailView):
#     model = Transaction


# class LedgersListView(PaginatedListMixin, ListView):
#     model = Transaction
#     template_name = "purchases/ledgers_list.html"


class TrackerListView(PaginatedListMixin, ListView):
    context_object_name = "tracker"
    queryset = Tracker.objects.all()
    list_filter = [
        ("carrier", RelatedFieldListViewFilter),
        ("purchase_request__requisitioner", RelatedFieldListViewFilter),
        ("purchase_request__vendor", RelatedFieldListViewFilter),
        ("purchase_request", RelatedFieldListViewFilter),
    ]


class TrackerCreateView(CreateView):
    form_class = TrackerForm
    template_name = "purchases/tracker_create.html"

    def get_initial(self):
        purchase_request_param = self.request.GET.get("purchase-request", None)
        if purchase_request_param:
            purchase_request = get_object_or_404(
                PurchaseRequest, slug=purchase_request_param
            )

        return {"purchase_request": purchase_request}

    def form_valid(self, form):
        if hasattr(form, "message"):
            messages.info(self.request, form.message)

        return super().form_valid(form)


class TrackerDetailView(DetailView):
    model = Tracker
    template_name = "purchases/tracker_detail.html"
    query_pk_and_slug = True


class TrackerDeleteView(DeleteView):
    model = Tracker
    success_url = reverse_lazy("tracker_list")

    def form_valid(self, *args, **kwargs):
        object = self.get_object()
        object.delete()

        redirect_url = redirect_to_next(self.request, "tracker_list")

        return redirect(redirect_url)
