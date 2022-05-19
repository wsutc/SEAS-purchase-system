from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.timezone import datetime,activate
from django.shortcuts import get_object_or_404
from .models import Manufacturer, Product, Vendor
from django.views.generic import ListView
from django.views.generic.detail import DetailView

from .forms import AddManufacturerForm, AddVendorForm, AddProductForm, NewPRForm


# Create your views here.
class HomeListView(ListView):
    model = Manufacturer

    def get_context_data(self, **kwargs):
        context = super(HomeListView, self).get_context_data(**kwargs)
        return context

class ProductListView(ListView):
    model = Product

    def get_context_data(self, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        return context

class VendorListView(ListView):
    model = Vendor

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

# def all_vendors(request):
#     vendors = Vendor.objects.all()
#     return render(request, 'purchases/all_vendors.html', {'vendors': vendors})

# def vendor_detail(request, slug):
#     vendor = get_object_or_404(Vendor, slug=slug)
#     return render(request, 'purchases/vendor_detail.html', {'vendor': vendor})

class VendorDetailView(DetailView):
    model = Vendor
    query_pk_and_slug = True

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

def new_pr(request):
    form = NewPRForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            pr = form.save(commit=False)
            pr.save()
            return redirect("home")
    else:
        return render(request, "purchases/new_pr.html", {"form": form})