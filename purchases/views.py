from itertools import product
from django.forms import formset_factory
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.timezone import datetime,activate
from django.shortcuts import get_object_or_404
from .models import Manufacturer, Product, PurchaseOrder, PurchaseRequest, PurchaseRequestItems, Vendor
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView

from .forms import AddManufacturerForm, AddVendorForm, AddProductForm, NewPRForm , ItemFormSet


# Create your views here.
class HomeListView(ListView):
    model = PurchaseRequest

    def get_context_data(self, **kwargs):
        context = super(HomeListView, self).get_context_data(**kwargs)
        return context

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
    model = PurchaseRequest

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

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
    # context_object_name: 'purchase_order_list'
    query_pk_and_slug = True

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

def add_product(request):
    form = AddProductForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            product = form.save(commit=False)
            # product.created_date = datetime.now()
            product.save()
            return redirect("home")
    else:
        return render(request, "purchases/add_product.html", {"form": form})

# def new_pr(request):
#     form = NewPRForm(request.POST or None)

#     if request.method == "POST":
#         if form.is_valid():
#             pr = form.save(commit=False)
#             pr.save()
#             return redirect("home")
#     else:
#         return render(request, "purchases/new_pr.html", {"form": form})

class PurchaseRequestCreateView(CreateView):
    model = PurchaseRequest
    form_class = NewPRForm
    template_name = 'purchases/new_pr.html'
    success_url = None
    # fields = (
    #     'requisitioner',
    #     'vendor',
    #     'items'
    # )

    # def get_context_data(self, **kwargs):
    #     context = super(PurchaseRequestCreateView, self).get_context_data(**kwargs)
    #     if self.request.POST:
    #         context['items'] = ItemFormSet(self.request.POST)
    #     else:
    #         context['items'] = ItemFormSet()
    #     return context

    def get_success_url(self):
            return reverse_lazy('purchaserequest_detail', kwargs={'id': self.object.id}) 

def manage_products(request):
    ProductFormSet = formset_factory(AddProductForm, extra=3)
    if request.method == 'POST':
        formset = ProductFormSet(request.POST, request.FILES)
        if formset.is_valid():
            pass
    else:
        formset = ProductFormSet()
    return render(request, 'purchases/manage_products.html', {'formset': formset})