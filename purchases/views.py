import base64
import hashlib
import hmac
from itertools import product
from django.conf import settings
from django.forms import formset_factory
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.timezone import datetime,activate
from django.shortcuts import get_object_or_404
from .models import Manufacturer, Product, PurchaseOrder, PurchaseRequest, PurchaseRequestItems, Requisitioner, Vendor, TrackingWebhookMessage
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.db.models import Sum, Count
from django.contrib.auth.mixins import PermissionRequiredMixin

import datetime as dt
import json
from secrets import compare_digest
from django.utils import timezone

from django.db.transaction import atomic, non_atomic_requests
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


from .forms import AddManufacturerForm, AddVendorForm, AddProductForm, NewPRForm , ItemFormSet, UpdateProductForm


# Create your views here.
class HomeListView(ListView):
    model = PurchaseRequest

    # def get_context_data(self, **kwargs):
    #     context = super(HomeListView, self).get_context_data(**kwargs)
    #     return context

class ManufacturerListView(ListView):
    model = Manufacturer

    def get_context_data(self, **kwargs):
        context = super(ManufacturerListView, self).get_context_data(**kwargs)
        return context

class ProductListView(ListView):
    model = Product

    def get_context_data(self, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        return context

class PurchaseRequestItemCreateView(CreateView):
    model = PurchaseRequestItems
    fields = [
        'product',
        'quantity',
        'price'
        ]

    success_url = "/"

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

class VendorListView(ListView):
    model = Vendor

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class PurchaseRequestListView(ListView):
    # model = PurchaseRequest
    context_object_name = 'purchaserequests'
    paginate_by = '10'
    queryset = PurchaseRequest.objects.order_by('-created_date')

    # def get_context_data(self, **kwargs):
    #     return super().get_context_data(**kwargs)

# def all_vendors(request):
#     vendors = Vendor.objects.all()
#     return render(request, 'purchases/all_vendors.html', {'vendors': vendors})

# def vendor_detail(request, slug):
#     vendor = get_object_or_404(Vendor, slug=slug)
#     return render(request, 'purchases/vendor_detail.html', {'vendor': vendor})

class VendorDetailView(DetailView):
    model = Vendor
    query_pk_and_slug = True

class ProductDetailView(DetailView):
    model = Product
    query_pk_and_slug = True

class ManufacturerDetailView(DetailView):
    model = Manufacturer
    query_pk_and_slug = True

class PurchaseRequestDetailView(DetailView):
    model = PurchaseRequest
    template_name = "purchases/purchaserequest_detail.html"
    context_object_name = 'purchaserequest'
    query_pk_and_slug = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['requisitioner_full_name'] = self.requisitioner_django.get_full_name()
        # context['requisitioner_full_name'] = PurchaseRequest.objects.filter(slug=self.kwargs.get('slug'))[0].requisitioner_django.get_full_name()
        # context['requisition_full_name'] = PurchaseRequest.objects.filter(slug=self.kwargs.get('slug'))[0].requisitioner.user.get_full_name()
    #     context['view_subtotal'] = PurchaseRequest.objects.filter(slug=self.kwargs.get('slug')).aggregate(Sum('purchaserequestitems__extended_price'))
    #     # context['requisitioner_full_name'] = PurchaseRequest.requisitioner.get_object(self)
    #     # print(self.kwargs.get('pk',-1))
    #     # print(context['view_subtotal'])
        print(context)
        return context

class PurchaseOrderDetailView(DetailView):
    model = PurchaseOrder
    query_pk_and_slug = True

# class PurchaseRequestCreateView(CreateView):
#     model = PurchaseRequest
#     widgets = {
#         'justification': forms.Textarea(attrs={'rows':2}),
#     }
#     fields = (
#             "requisitioner",
#             "items",
#             "need_by_date",
#             "tax_exempt",
#             "accounts",
#             "shipping",
#             "justification",
#             "instruction",
#             "purchase_type",
#             "number"
#         )

def add_mfg(request):
    form = AddManufacturerForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            manufacturer = form.save(commit=False)
            # manufacturer.created_date = datetime.now()
            manufacturer.save()
            return redirect("home")
    else:
        return render(request, "purchases/add_manufacturer.html", {"form": form})

def add_vendor(request):
    form = AddVendorForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            vendor = form.save(commit=False)
            # vendor.created_date = datetime.now()
            vendor.save()
            return redirect("home")
    else:
        return render(request, "purchases/add_vendor.html", {"form": form})

# def add_product(request):
#     form = AddProductForm(request.POST or None)

#     if request.method == "POST":
#         if form.is_valid():
#             product = form.save(commit=False)
#             # product.created_date = datetime.now()
#             product.save()
#             return # redirect("home")
#     else:
#         return render(request, "purchases/add_product.html", {"form": form})

# def new_pr(request):
#     form = NewPRForm(request.POST or None)

#     if request.method == "POST":
#         if form.is_valid():
#             pr = form.save(commit=False)
#             pr.save()
#             return redirect("home")
#     else:
#         return render(request, "purchases/new_pr.html", {"form": form})

class ProductUpdateView(UpdateView):
    model = Product
    form_class = UpdateProductForm
    template_name = 'purchases/add_product.html'

class ProductCreateView(CreateView):
    form_class = AddProductForm
    template_name = 'purchases/add_product.html'

class PurchaseRequestCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'purchases.add_purchaserequest'
    # model = PurchaseRequest
    form_class = NewPRForm
    template_name = 'purchases/new_pr.html'

    def get_context_data(self, **kwargs):
        context = super(PurchaseRequestCreateView, self).get_context_data(**kwargs)
        context['purchase_request_items_formset'] = ItemFormSet()
        # context['requisitioner'] = Requisitioner.objects.get(user=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        purchase_request_items_formset = ItemFormSet(self.request.POST)
        if form.is_valid() and purchase_request_items_formset.is_valid():
            return self.form_valid(form, purchase_request_items_formset)
        else:
            return self.form_invalid(form, purchase_request_items_formset)

    def form_valid(self, form, purchase_request_items_formset):
        form.instance.requisitioner = Requisitioner.objects.get(user = self.request.user)
        self.object = form.save(commit=False)
        self.object.save()
        purchase_request_items = purchase_request_items_formset.save(commit=False)
        for item in purchase_request_items:
            item.purchase_request = self.object
            item.save()
        self.object.update_totals()
        return redirect(reverse_lazy("home"))

    def form_invalid(self, form, purchase_request_items_formset):
        return self.render_to_response(
            self.get_context_data(
                form=form,
                purchase_request_items_formset=purchase_request_items_formset
            )
        )

class PurchaseRequestUpdateView(UpdateView):
    # permission_required = 'purchases.change_purchaserequest'
    model = PurchaseRequest
    form_class = NewPRForm
    template_name = 'purchases/new_pr.html'

    def get_context_data(self, **kwargs):
        context = super(PurchaseRequestUpdateView, self).get_context_data(**kwargs)
        context['purchase_request_items_formset'] = ItemFormSet()
        context['requisitioner'] = PurchaseRequest.objects.get(slug=self.kwargs['slug']).requisitioner
    #     context['requisitioner'] = self.
    #     # context['requisitioner'] = Requisitioner.objects.get(user=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        purchase_request_items_formset = ItemFormSet(self.request.POST)
        if form.is_valid() and purchase_request_items_formset.is_valid():
            return self.form_valid(form, purchase_request_items_formset)
        else:
            return self.form_invalid(form, purchase_request_items_formset)

    def form_valid(self, form, purchase_request_items_formset):
        # form.instance.requisitioner = Requisitioner.objects.get(user = self.request.user)
        self.object = form.save(commit=False)
        self.object.save()
        purchase_request_items = purchase_request_items_formset.save(commit=False)
        for item in purchase_request_items:
            item.purchase_request = self.object
            item.save()
        self.object.update_totals()
        return redirect(reverse_lazy("purchaserequest_detail/<slug:self.object.slug>"))

    def form_invalid(self, form, purchase_request_items_formset):
        return self.render_to_response(
            self.get_context_data(
                form=form,
                purchase_request_items_formset=purchase_request_items_formset,
            )
        )

def manage_products(request):
    ProductFormSet = formset_factory(AddProductForm, extra=3)
    if request.method == 'POST':
        formset = ProductFormSet(request.POST, request.FILES)
        if formset.is_valid():
            pass
    else:
        formset = ProductFormSet()
    return render(request, 'purchases/manage_products.html', {'formset': formset})



@csrf_exempt
@require_POST
@non_atomic_requests
def tracking_webhook(request):
    secret = settings.AFTERSHIP_WEBHOOK_SECRET
    given_token = request.headers.get("aftership-hmac-sha256", "")
    # token_byte = bytes(settings.AFTERSHIP_WEBHOOK_SECRET, 'UTF-8')
    # hmac_raw = hmac.new(token_byte, digestmod=hashlib.sha256)
    # hash = base64.b64encode(hmac_raw.digest()).decode()
    signature = generate_signature(secret,request.body)
    if not compare_digest(given_token, signature):
        return HttpResponseForbidden(
            "Incorrect token in Aftership-Hmac-Sha256 header.",
            content_type="text/plain"
        )

    TrackingWebhookMessage.objects.filter(
        received_at__lte = timezone.now() - dt.timedelta(days=7)
    ).delete()

    payload = json.loads(request.body)
    TrackingWebhookMessage.objects.create(
        received_at=timezone.now(),
        payload=payload
    )

    process_webhook_payload(payload)

    return HttpResponse("Message successfully received.", content_type="text/plain")

@atomic
def process_webhook_payload(payload):
    # TODO: stuff
    # purchase_order = PurchaseOrder.objects.get(tracker_id=payload['msg']['id'])
    # print(purchase_order.number)

    pass

def generate_signature(secret,payload):
    # given_token = request.headers.get("aftership-hmac-sha256", "")
    # body = request.body
    token_byte = bytes(secret, 'UTF-8')
    hashBytes = hmac.new(token_byte, payload, digestmod=hashlib.sha256)
    hash = base64.b64encode(hashBytes.digest()).decode()

    return hash