import datetime as dt
import io
import json
import logging
import os
from functools import partial
from importlib.metadata import version

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.transaction import atomic, non_atomic_requests
from django.http import FileResponse, HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy  # , reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import ListView  # , View
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django_listview_filters.filters import (
    AllValuesFieldListFilter,
    ChoicesFieldListViewFilter,
    RelatedFieldListViewFilter,
)
from furl import furl
from packaging import version as p_version
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm, inch
from reportlab.pdfgen import canvas
from reportlab.platypus import PageTemplate, SimpleDocTemplate, Table, TableStyle
from reportlab.platypus.frames import Frame
from reportlab.platypus.paragraph import Paragraph

from purchases.forms import (
    AddVendorForm,
    AddVendorOrderForm,
    CreateUserForm,
    CustomPurchaseRequestForm,
    NewPRForm,
    PurchaseRequestAccountsFormset,
    SimpleProductCopyForm,
    SimpleProductFormset,
    TrackerForm,
)
from purchases.models import (
    Accounts,
    Balance,
    Carrier,
    PurchaseRequest,
    Requisitioner,
    SimpleProduct,
    Status,
    Tracker,
    TrackingWebhookMessage,
    Transaction,
    Vendor,
    VendorOrder,
    requisitioner_from_user,
)
from purchases.tracking import (
    TrackerObject,
    get_generated_signature,
    update_tracking_details,
)
from web_project.helpers import PaginatedListMixin, redirect_to_next, truncate_string

# from fdfgen import forge_fdf


logger = logging.getLogger(__name__)

# Create your views here.


# class VendorListView(PaginatedListMixin, ListView):
#     context_object_name = "vendors"
#     queryset = Vendor.objects.order_by("name")


# class SimpleView(SingleObjectMixin):
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)

#         context["purchase_request_statuses"] = Status.objects.filter(
#             parent_model="PR"
#         ).order_by("rank")

#         return context


# class VendorOrderCreateView(CreateView):
#     form_class = AddVendorOrderForm
#     template_name = "purchases/vendororder_create.html"

#     def form_valid(self, form):
#         if hasattr(form, "message"):
#             messages.info(self.request, form.message)

#         return super().form_valid(form)


# class VendorOrderDetailView(SimpleView, DetailView):
#     model = VendorOrder
#     query_pk_and_slug = True

#     # def get_context_data(self, **kwargs):
#     #     context = super().get_context_data(**kwargs)

#     #     # trackers = []
#     #     # object = self.get_object()
#     #     # for request in object.purchase_requests.all():
#     #     #     for tracker in request.tracker_set.all():
#     #     #         trackers.append(tracker)

#     #     # context['trackers'] = trackers

#     #     return context


# class VendorOrderListView(PaginatedListMixin, ListView):
#     context_object_name = "vendororder"
#     queryset = VendorOrder.objects.all()
#     list_filter = [
#         ("purchase_requests", RelatedFieldListViewFilter),
#         ("vendor", RelatedFieldListViewFilter),
#         ("purchase_requests__requisitioner", RelatedFieldListViewFilter),
#         ("purchase_requests__status", ChoicesFieldListViewFilter),
#         # ("o.purchase_requests.last.tracker_set.last.status"),
#     ]


# class VendorOrderCurrentListView(VendorOrderListView):
#     template_name = "purchases/vendororder_current_list.html"
#     queryset = VendorOrder.objects.filter(purchase_requests__status__open=True)


# class SimpleProductListView(PaginatedListMixin, ListView):
#     context_object_name = "simpleproduct"
#     queryset = SimpleProduct.objects.order_by("purchase_request__vendor", "name")
#     list_filter = [
#         ("purchase_request__vendor", RelatedFieldListViewFilter),
#         ("purchase_request__requisitioner", RelatedFieldListViewFilter),
#         ("purchase_request__status", ChoicesFieldListViewFilter),
#         ("purchase_request", RelatedFieldListViewFilter),
#         # ("purchase_request__tracker_set__latest__status", AllValuesFieldListFilter),
#     ]

#     def get_context_data(self, **kwargs):
#         """Add context for max digits of unit price field for formatting."""
#         context = super().get_context_data(**kwargs)

#         def count_digits(value) -> int:
#             string = f"{float(value)}"
#             parts = string.split(".")
#             if len(parts) > 1:
#                 decimals = parts[1]
#                 return len(decimals)
#             else:
#                 return 0

#         filter_name = "purchase_request__vendor"

#         dlf_version_str = version("django_listview_filters")

#         if p_version.parse(dlf_version_str) <= p_version.parse("0.0.1b0.dev1"):
#             filter = [
#                 filter
#                 for filter in self.filter_specs
#                 if filter.field_path == filter_name
#             ][0]
#         else:
#             filter = self.get_filter_by_name(filter_name)

#         filter.lookup_choices = sorted(
#             filter.lookup_choices, key=lambda x: x[1].lower()
#         )

#         if settings.DEBUG:
#             for counter, choice in enumerate(filter.lookup_choices):
#                 logger.debug(f"Choice {counter}: {choice}")

#         qs = context["object_list"]

#         unitprice_values = qs.values_list("unit_price", flat=True)

#         digits_list = []
#         for value in unitprice_values:
#             digits = count_digits(value)
#             digits_list.append(digits)

#         logger.debug(f"Object List Length: {len(digits_list)}")

#         context["unitprice_maxdigits"] = max(digits_list)

#         return context


# class SimpleProductPRListView(SimpleProductListView):
#     # queryset = SimpleProduct.objects.order_by("purchase_request__vendor", "name")
#     list_filter = []

#     def get_queryset(self):
#         qs = super().get_queryset()
#         slug = self.kwargs["purchaserequest"]
#         purchase_request = PurchaseRequest.objects.filter(slug=slug)
#         qs = qs.filter(purchase_request__in=purchase_request)

#         logger.warning(f"Purchase Request: {purchase_request.first()}")

#         return qs


# class PurchaseRequestListViewBase(PaginatedListMixin, ListView):
#     context_object_name = "purchaserequests"
#     queryset = PurchaseRequest.objects.order_by("-created_date")
#     list_filter = [
#         ("status", RelatedFieldListViewFilter),
#         ("vendor", RelatedFieldListViewFilter),
#         ("requisitioner", RelatedFieldListViewFilter),
#     ]

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["purchase_request_statuses"] = Status.objects.filter(
#             parent_model="PR"
#         ).order_by("rank")
#         return context

#     class Meta:
#         abstract = True


# class PurchaseRequestListView(PurchaseRequestListViewBase):
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)

#         context["show_link"] = (_("show open"), "open_pr")

#         return context


# class RequisitionerPurchaseRequestListView(PurchaseRequestListViewBase):
#     # filters = [
#     #     ("status", {'field':'status', 'parent_model':PurchaseRequest}),
#     #     ("vendor", {'model':Vendor, 'parent_model':PurchaseRequest, 'field':'purchaserequest', 'order_by':'name'}),
#     # ]
#     list_filter = [
#         ("status", ChoicesFieldListViewFilter),
#         ("vendor", RelatedFieldListViewFilter),
#     ]

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)

#         context["show_link"] = (_("show open"), "open_pr")

#         return context

#     def get_queryset(self):
#         self.requisitioner = get_object_or_404(
#             Requisitioner, slug=self.kwargs["requisitioner"]
#         )
#         qs = PurchaseRequest.objects.filter(requisitioner=self.requisitioner).order_by(
#             "-created_date"
#         )

#         qs = self.filter_queryset(qs)

#         return qs


# class OpenPurchaseRequestListView(PurchaseRequestListViewBase):
#     # pr = PurchaseRequest.PurchaseRequestStatuses
#     # current_statuses = [pr.WL, pr.AP, pr.OR, pr.PT, pr.SH, pr.AA]
#     queryset = PurchaseRequest.objects.filter(status__open=True).order_by(
#         "-created_date"
#     )
#     list_filter = [
#         ("vendor", RelatedFieldListViewFilter),
#         ("requisitioner", RelatedFieldListViewFilter),
#     ]

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)

#         context["show_link"] = (_("show all"), "home")

#         return context


# class PurchaseRequestDetailView(SimpleView, DetailView):
#     model = PurchaseRequest
#     template_name = "purchases/purchaserequest_detail.html"
#     context_object_name = "purchaserequest"
#     query_pk_and_slug = True

#     def get_context_data(self, **kwargs):
#         """Add context for max digits of unit price field for formatting."""
#         context = super().get_context_data(**kwargs)

#         def count_digits(value) -> int:
#             string = f"{float(value)}"
#             parts = string.split(".")
#             if len(parts) > 1:
#                 decimals = parts[1]
#                 return len(decimals)
#             else:
#                 return 0

#         # context["purchase_request_statuses"] = get_status_choices()

#         unitprice_values = self.object.simpleproduct_set.values_list(
#             "unit_price", flat=True
#         )

#         digits_list = []
#         for value in unitprice_values:
#             digits = count_digits(value)
#             digits_list.append(digits)

#         context["simpleproducts_unitprice_maxdigits"] = max(digits_list)

#         return context


# class RequisitionerCreateView(CreateView):
#     form_class = CreateUserForm
#     template_name = "purchases/requisitioner_create.html"

#     def form_valid(self, form):
#         user = form.save()
#         user.refresh_from_db()

#         user.requisitioner.wsu_id = form.cleaned_data.get("wsu_id")
#         user.save()

#         return redirect(user.requisitioner)


# class RequisitionerDetailView(DetailView):
#     model = Requisitioner
#     template_name = "purchases/requisitioner_detail.html"
#     query_pk_and_slug = True


# class RequisitionerListView(PaginatedListMixin, ListView):
#     context_object_name = "requisitioners"
#     admin_user = User.objects.filter(username="admin").first()
#     queryset = Requisitioner.objects.exclude(user=admin_user).order_by("user")


# class RequisitionerUpdateView(UpdateView):
#     model = Requisitioner
#     form_class = CreateUserForm
#     template_name = "purchases/requisitioner_create.html"
#     query_pk_and_slug = True


# class VendorDeleteView(DeleteView):
#     model = Vendor
#     success_url = reverse_lazy("all_vendors")

#     def form_valid(self, *args, **kwargs):
#         object = self.get_object()
#         object.delete()

#         redirect_url = redirect_to_next(self.request, "all_vendors")

#         return redirect(redirect_url)


# class VendorCreateView(CreateView):
#     form_class = AddVendorForm
#     template_name = "purchases/add_vendor.html"


# # class VendorModalCreateView(BSModalCreateView):
# #     template_name = 'purchases/vendor_create_modal.html'
# #     form_class = VendorModelForm
# #     success_message = 'Success: New Vendor created.'


# class PurchaseRequestCreateView(PermissionRequiredMixin, CreateView):
#     permission_required = "purchases.add_purchaserequest"
#     form_class = NewPRForm
#     template_name = "purchases/new_pr.html"

#     def get_initial(self):
#         req_obj = requisitioner_from_user(self.request.user)
#         self.initial.update({"requisitioner": req_obj})
#         return super().get_initial()

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["purchase_request_items_formset"] = SimpleProductFormset(prefix="items")
#         context["purchase_request_accounts_formset"] = PurchaseRequestAccountsFormset(
#             prefix="accounts"
#         )
#         # context['requisitioner'] = Requisitioner.objects.get(user=self.request.user)
#         return context

#     def post(self, request, *args, **kwargs):
#         self.object = None
#         form_class = self.get_form_class()
#         form = self.get_form(form_class)
#         purchase_request_items_formset = SimpleProductFormset(
#             self.request.POST, prefix="items"
#         )
#         purchase_request_accounts_formset = PurchaseRequestAccountsFormset(
#             self.request.POST, prefix="accounts"
#         )
#         if not (priValid := purchase_request_items_formset.is_valid()):
#             print(purchase_request_items_formset.errors)
#         if not (praValid := purchase_request_accounts_formset.is_valid()):
#             print(purchase_request_accounts_formset.errors)
#         if form.is_valid() and priValid and praValid:
#             return self.form_valid(
#                 form, purchase_request_items_formset, purchase_request_accounts_formset
#             )
#         else:
#             return self.form_invalid(
#                 form, purchase_request_items_formset, purchase_request_accounts_formset
#             )

#     def form_valid(
#         self, form, purchase_request_items_formset, purchase_request_accounts_formset
#     ):
#         self.object = form.save(commit=False)
#         self.object.save()

#         ## Add Items
#         purchase_request_items = purchase_request_items_formset.save(commit=False)
#         for item in purchase_request_items:
#             item.purchase_request = self.object
#             item.save()

#         ## Add Accounts
#         purchase_request_accounts = purchase_request_accounts_formset.save(commit=False)
#         for account in purchase_request_accounts:
#             account.purchase_request = self.object
#             account.save()

#         # # Set PR totals and update balance (balance isn't functional)
#         self.object.update_totals()

#         return redirect(self.object)

#     def form_invalid(
#         self, form, purchase_request_items_formset, purchase_request_accounts_formset
#     ):
#         return self.render_to_response(
#             self.get_context_data(
#                 form=form,
#                 purchase_request_items_formset=purchase_request_items_formset,
#                 purchase_request_accounts_formset=purchase_request_accounts_formset,
#             )
#         )


# class CustomPurchaseRequestCreateView(PermissionRequiredMixin, CreateView):
#     permission_required = "purchases.add_purchaserequest"
#     form_class = CustomPurchaseRequestForm
#     template_name = "purchases/new_pr.html"

#     def get_initial(self):
#         req_obj = requisitioner_from_user(self.request.user)
#         self.initial.update({"requisitioner": req_obj})
#         return super().get_initial()

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["purchase_request_items_formset"] = SimpleProductFormset(prefix="items")
#         context["purchase_request_accounts_formset"] = PurchaseRequestAccountsFormset(
#             prefix="accounts"
#         )
#         # context['requisitioner'] = Requisitioner.objects.get(user=self.request.user)
#         return context

#     def post(self, request, *args, **kwargs):
#         self.object = None
#         form_class = self.get_form_class()
#         form = self.get_form(form_class)
#         purchase_request_items_formset = SimpleProductFormset(
#             self.request.POST, prefix="items"
#         )
#         purchase_request_accounts_formset = PurchaseRequestAccountsFormset(
#             self.request.POST, prefix="accounts"
#         )
#         if not (priValid := purchase_request_items_formset.is_valid()):
#             print(purchase_request_items_formset.errors)
#         if not (praValid := purchase_request_accounts_formset.is_valid()):
#             print(purchase_request_accounts_formset.errors)
#         if form.is_valid() and priValid and praValid:
#             return self.form_valid(
#                 form, purchase_request_items_formset, purchase_request_accounts_formset
#             )
#         else:
#             return self.form_invalid(
#                 form, purchase_request_items_formset, purchase_request_accounts_formset
#             )

#     def form_valid(
#         self, form, purchase_request_items_formset, purchase_request_accounts_formset
#     ):
#         self.object = form.save(commit=False)
#         self.object.save()

#         ## Add Items
#         purchase_request_items = purchase_request_items_formset.save(commit=False)
#         for item in purchase_request_items:
#             item.purchase_request = self.object
#             item.save()

#         ## Add Accounts
#         purchase_request_accounts = purchase_request_accounts_formset.save(commit=False)
#         for account in purchase_request_accounts:
#             account.purchase_request = self.object
#             account.save()

#         # # Set PR totals and update balance (balance isn't functional)
#         self.object.update_totals()

#         return redirect(self.object)

#     def form_invalid(
#         self, form, purchase_request_items_formset, purchase_request_accounts_formset
#     ):
#         return self.render_to_response(
#             self.get_context_data(
#                 form=form,
#                 purchase_request_items_formset=purchase_request_items_formset,
#                 purchase_request_accounts_formset=purchase_request_accounts_formset,
#             )
#         )


# class PurchaseRequestUpdateView(UpdateView):
#     permission_required = "purchases.change_purchaserequest"
#     model = PurchaseRequest
#     form_class = NewPRForm
#     template_name = "purchases/purchaserequest_update.html"
#     query_pk_and_slug = True

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         if self.request.POST:
#             context["purchase_request_items_formset"] = SimpleProductFormset(
#                 self.request.POST, instance=self.object, prefix="items"
#             )
#             context[
#                 "purchase_request_accounts_formset"
#             ] = PurchaseRequestAccountsFormset(
#                 self.request.POST, instance=self.object, prefix="accounts"
#             )
#         else:
#             context["purchase_request_items_formset"] = SimpleProductFormset(
#                 instance=self.object, prefix="items"
#             )
#             context[
#                 "purchase_request_accounts_formset"
#             ] = PurchaseRequestAccountsFormset(instance=self.object, prefix="accounts")
#         return context

#     def form_valid(self, form):
#         context = self.get_context_data()
#         self.object = form.save(commit=False)

#         purchase_request_items_formset = context["purchase_request_items_formset"]
#         purchase_request_accounts_formset = context["purchase_request_accounts_formset"]

#         if not purchase_request_items_formset.is_valid():
#             return self.form_invalid(form)
#         if not purchase_request_accounts_formset.is_valid():
#             return self.form_invalid(form)

#         purchase_request_items_formset.save(commit=True)
#         purchase_request_accounts_formset.save(commit=True)

#         self.object.save()

#         self.object.update_totals()

#         return redirect(self.object)

#     def form_invalid(self, form):
#         context = self.get_context_data()
#         return self.render_to_response(
#             self.get_context_data(
#                 form=form,
#                 purchase_request_items_formset=context[
#                     "purchase_request_items_formset"
#                 ],
#                 purchase_request_accounts_formset=context[
#                     "purchase_request_accounts_formset"
#                 ],
#             )
#         )


# class AccountDetailView(SimpleView, DetailView):
#     model = Accounts
#     template_name = "purchases/account_detail_simple.html"


def update_pr_status(request: HttpRequest, slug: str, *args, **kwargs) -> HttpResponse:
    new_status = request.GET.get("status", None)

    redirect_url = redirect_to_next(request, "purchaserequest_detail", slug=slug)
    return_redirect = redirect(redirect_url)

    if not new_status:
        messages.info(_("existing status chosen, no changes made."))
        return return_redirect

    status = Status.objects.filter(pk=new_status).first()

    qs = PurchaseRequest.objects.filter(slug=slug)
    count = qs.count()
    if count == 1:
        qs.update(status=status)
        messages.add_message(
            request,
            messages.SUCCESS,
            message="{pr}'s status updated to '{status}.'".format(
                pr=qs.first(), status=status.name.title()
            ),
        )
    else:
        logger.warning(
            "Slug {} returned too many/too few results: {}; no records updated.".format(
                slug,
                count,
            )
        )
        messages.add_message(
            request,
            messages.ERROR,
            message="Slug returned too many/too few results: {}; no records updated.".format(
                count
            ),
        )

    return return_redirect


@csrf_exempt
@require_POST
@non_atomic_requests
def tracking_webhook(request):

    if request.method == "HEAD":
        response = HttpResponse(
            "Message successfully received.", content_type="text/plain"
        )
        return response
    else:
        secret = settings._17TRACK_KEY
        given_token = request.headers.get("sign", "")

        if get_generated_signature(request.body, secret) != given_token:
            return HttpResponseForbidden(
                "Inconsistency in response signature.", content_type="text/plain"
            )

        deleted, _ = TrackingWebhookMessage.objects.filter(
            received_at__lte=timezone.now() - dt.timedelta(days=7)
        ).delete()

        if deleted > 0:
            logger.info(f"Webhook Messages Deleted: {deleted}")
        else:
            logger.info("No Webhook Messages Deleted.")

        payload = json.loads(request.body)
        TrackingWebhookMessage.objects.create(
            received_at=timezone.now(), payload=payload
        )

        try:
            success, message = process_webhook_payload(payload)
            if success:
                logger.info(message)
            else:
                logger.warning(message)
        except ObjectDoesNotExist:
            logger.error("No object matching payload found", exc_info=1)

        return HttpResponse("Message successfully received.", content_type="text/plain")


@atomic
def process_webhook_payload(payload: dict) -> str:
    event_type = payload.get("event")

    if event_type == "TRACKING_UPDATED":
        payload_obj = TrackerObject.fromupdateresponse(payload.get("data"))

        try:
            carrier, _ = Carrier.objects.get_or_create(
                carrier_code=payload_obj.carrier_code,
                defaults={"name": payload_obj.carrier_name},
            )
            tracker, _ = Tracker.objects.get_or_create(
                tracking_number=payload_obj.tracking_number, carrier=carrier
            )
        except ObjectDoesNotExist:
            raise

        if tracker.events_hash != str(payload_obj.events_hash):
            _, _ = tracker.create_events(payload_obj.events)

        success = tracker.update_tracker_fields(payload_obj)

        tracker_success = f"Tracker {tracker} successfully updated."
        tracker_failure = f"No updates made to tracker {tracker}."

        return success, tracker_success if success else tracker_failure

    elif event_type == "TRACKING_STOPPED":
        payload_obj = TrackerObject.fromstopresponse(payload.get("data"))

        try:
            carrier = Carrier.objects.get(carrier_code=payload_obj.carrier_code)
            tracker = Tracker.objects.get(
                tracking_number=payload_obj.tracking_number, carrier=carrier
            )
        except ObjectDoesNotExist:
            raise

        stop = tracker.stop()

        success_message = f"Tracker {tracker} successfully stopped."
        failure_message = "No trackers stopped."

        return stop, success_message if stop else failure_message


def generate_pr_pdf(request, slug):
    purchase_request = PurchaseRequest.objects.get(slug=slug)
    buffer = io.BytesIO()

    def header(canvas: canvas, doc, content):
        """Creates header from flowable?"""
        canvas.saveState()
        w, h = content.wrap(doc.width, doc.topMargin)
        content.drawOn(
            canvas, doc.leftMargin, doc.height + doc.bottomMargin + doc.topMargin - h
        )
        canvas.restoreState()

    def footer(canvas: canvas, doc, content):
        """Creates footer from flowable?"""
        canvas.saveState()
        w, h = content.wrap(doc.width, doc.bottomMargin)
        content.drawOn(canvas, doc.leftMargin, h)
        canvas.restoreState()

    def header_and_footer(canvas: canvas, doc, header_content, footer_content):
        """Need to build both header AND footer in same function"""
        header(canvas, doc, header_content)
        footer(canvas, doc, footer_content)

    styles = getSampleStyleSheet()

    styles_title = styles["Title"]
    styles_title.name = "Header-Title"
    styles_title.fontSize = 40
    styles_title.textColor = colors.HexColor("#CA1237")

    # Set header styles
    styles.add(styles_title)

    # style_header_normal = styles['Normal']
    # style_header_title = styles['Title']
    # style_header_title.fontSize = 40

    # Set footer styles
    # style_footer_normal = styles['Normal']

    filename = purchase_request.number + ".pdf"

    doc = SimpleDocTemplate(buffer, pagesize=letter, title=purchase_request.number)

    doc.leftMargin = doc.rightMargin = 1 * cm
    # doc.rightMargin = 42
    doc.width = doc.pagesize[0] - doc.leftMargin - doc.rightMargin

    frame = Frame(
        doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal"
    )  # , showBoundary=1)

    header_content = Paragraph(purchase_request.number, styles["Header-Title"])
    footer_content = Paragraph("This is a footer", styles["Normal"])

    template = PageTemplate(
        id="test",
        frames=frame,
        onPage=partial(
            header_and_footer,
            header_content=header_content,
            footer_content=footer_content,
        ),
    )

    doc.addPageTemplates([template])

    elements = []

    # Define purchase request information table
    info_column_widths = [0.9 * inch, 2.4 * inch, 0.9 * inch, 2.4 * inch]

    # link = '<link href="' + purchase_request.vendor.website + '">' + purchase_request.vendor.website + '</link>'

    # <td rowspan=2>{{ object.vendor.street1 }}<br>
    #                             {% if object.vendor.street2 %}
    #                                 {{ object.vendor.street2 }}<br>
    #                             {% endif %}
    #                             {% if object.vendor.city %}
    #                                 {{ object.vendor.city }}, {{ object.vendor.state.abbreviation }} {{ object.vendor.zip }}
    #                             {% else %}
    #                             {% endif %}
    #                         </td>
    vendor = purchase_request.vendor
    address_line = ""
    if hasattr(vendor.state, "abbreviation"):
        address_line += str(vendor.state.abbreviation)
        if city := vendor.city:
            address_line = str(city) + ", " + address_line + " " + str(vendor.zip)
            if street2 := vendor.street2:
                address_line = str(street2) + "\n" + address_line
            if street1 := vendor.street1:
                address_line = str(street1) + "\n" + address_line

    info_data = [
        [
            "Needed By",
            purchase_request.need_by_date,
            "Requestor",
            purchase_request.requisitioner.user.get_full_name(),
        ],
        [
            "Vendor",
            purchase_request.vendor.name,
            "Email",
            purchase_request.requisitioner.user.email,
        ],
        ["Address", address_line, "Phone", purchase_request.requisitioner.phone],
        ["", "", "Department", purchase_request.requisitioner.department.code],
        ["Phone", purchase_request.vendor.phone],
        ["Email", purchase_request.vendor.email],
        ["Website", purchase_request.vendor.website],
    ]

    info_table = Table(info_data, info_column_widths)

    info_table.setStyle(
        TableStyle(
            [
                # ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
                # ('ALIGN',(0,0),(-1,0),'CENTER'),
                # ('LINEBELOW',(0,0),(-1,-1),0.5,colors.black),
                # ('FONTNAME',(0,1),(-1,0),'Helvetica'),
                # ('ALIGN',(1,1),(-3,-1),'CENTER'),
                ("ALIGN", (0, 0), (0, -1), "RIGHT"),
                ("VALIGN", (0, 2), (1, 2), "TOP"),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("ALIGN", (2, 0), (2, -1), "RIGHT"),
                ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
                ("SPAN", (0, 2), (0, 3)),
                ("SPAN", (1, 2), (1, 3)),
                # ('ROWBACKGROUNDS',(0,1),(-1,-5),[colors.aliceblue,colors.white]),
                # ('BOX',(0,0),(-1,-1),0.5,colors.black),
                ("SPAN", (2, 4), (-1, -1)),
                # ('INNERGRID',(0,0),(-1,-5),0.1,colors.darkgray),
                # ('BOX',(-3,-4),(-1,-1),0.5,colors.black),
                # ('ALIGN',(-3,-4),(-1,-1),'RIGHT'),
                # ('LINEABOVE',(-3,-1),(-1,-1),0.1,colors.darkgray),
                # ('SPAN',(0,-4),(3,-1)),
                # ('SPAN',(-3,-4),(-2,-4))
            ]
        )
    )

    elements.append(info_table)

    # Define Table
    data = [
        ["Description", "Identifier", "Vendor ID", "QTY", "Unit", "Price", "Ext. Price"]
    ]

    # Create rows for each item
    data = appendAsList(data, item_rows(purchase_request))

    # Create rows showing subtotal, shipping, tax, and grand total
    total_rows = [
        ["", "", "", "", "", "Subtotal", purchase_request.subtotal],
        ["", "", "", "", "", "Shipping", purchase_request.shipping],
        ["", "", "", "", "", "Tax", purchase_request.sales_tax],
        ["", "", "", "", "", "Grand Total", purchase_request.grand_total],
    ]

    data = appendAsList(data, total_rows)

    # Create a 'standardized width' [sw] that is 1% of the doc.width
    sw = doc.width / 100

    # Use the sw to generate a table that is exactly the same width as doc.width
    column_widths = [38 * sw, 14 * sw, 14 * sw, 7 * sw, 7 * sw, 8 * sw, 12 * sw]

    items_table = Table(data, colWidths=column_widths)  # Create table

    # Set style for table and rows
    items_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.black),
                ("FONTNAME", (0, 1), (-1, 0), "Helvetica"),
                ("ALIGN", (1, 1), (-3, -1), "CENTER"),
                ("ALIGN", (-2, 1), (-1, -5), "RIGHT"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -5), [colors.aliceblue, colors.white]),
                ("BOX", (0, 0), (-1, -5), 0.5, colors.black),
                ("INNERGRID", (0, 0), (-1, -5), 0.1, colors.darkgray),
                # ('BOX',(-3,-4),(-1,-1),0.5,colors.black),
                ("ALIGN", (-3, -4), (-1, -1), "RIGHT"),
                ("LINEABOVE", (-3, -1), (-1, -1), 0.1, colors.darkgray),
                # ('SPAN',(0,-4),(3,-1)),
                # ('SPAN',(-3,-4),(-2,-4))
            ]
        )
    )

    # Add items_table to 'elements' list
    elements.append(items_table)

    doc.build(elements)

    # doc.showPage()
    # doc.save()

    buffer.seek(0)

    return FileResponse(buffer, as_attachment=True, filename=filename)


# ------------------ NOT CURRENTLY USED ----------------------------
# def get_image(filename: str, url: str):
#     """Get an image for the PDF"""
#     if not os.path.exists(filename):
#         response = HttpResponse()


def appendAsList(data: list[list:str], list: list[list:str]):
    for i in list:
        data.append(i)

    return data


def item_rows(purchase_request: PurchaseRequest):
    """Create nested list of items to be used in a table"""
    items = purchase_request.simpleproduct_set.all()
    rows = []
    for i in items:
        row = [
            truncate_string(i.name, 40),
            i.identifier,
            "",
            i.quantity,
            i.unit,
            i.unit_price,
            i.extended_price,
        ]
        rows.append(row)

    return rows


def fill_pr_pdf(request, purchase_request: PurchaseRequest):
    pass


def update_balance(request, pk: int):
    balance = get_object_or_404(Balance, pk=pk)
    balance.recalculate_balance()

    return redirect("balances_list")


def update_tracker(request, pk, *args, **kwargs):
    fragment = furl(request.get_full_path())
    # TODO: not properly identifying whether any new information was obtained
    tracker = get_object_or_404(Tracker, pk=pk)

    try:
        if tracker.carrier:
            response = update_tracking_details(
                [(tracker.tracking_number, tracker.carrier.carrier_code)]
            )
        else:
            response = update_tracking_details([(tracker.tracking_number, None)])

        data = next(iter(response or []), None)
    except Exception as err:
        messages.error(request, f"{err}")

    if data.get("code") == 0:
        tracker_obj = data.get("tracker")

        if tracker_obj.events_hash != tracker.events_hash:
            _, _ = tracker.create_events(tracker_obj.events)

        tracker_str = tracker.tracking_number.upper()

        count = tracker.update_tracker_fields(tracker_obj)
        if count:
            messages.success(
                request,
                f"Tracker '{tracker_str}' updated with new information.",
            )
        elif tracker_obj.status == "NotFound":
            messages.warning(
                request,
                "Tracker '{}' was not found, please check the tracking number and carrier ({}).".format(
                    tracker_str, tracker_obj.carrier_name
                ),
            )
        else:
            messages.info(request, f"Tracker '{tracker_str}' was already up to date.")

    url = tracker if "next" not in fragment.args else fragment.args.get("next")

    # url = tracker if not fragment.args.has_key("next") else fragment.args.get("next")

    return redirect(url)
