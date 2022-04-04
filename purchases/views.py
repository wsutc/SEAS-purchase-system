from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.timezone import datetime,activate
from purchases.models import Manufacturer, Product
from django.views.generic import ListView

from purchases.forms import AddManufacturerForm, AddVendorForm, AddProductForm, NewPRForm


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