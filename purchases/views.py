from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.timezone import datetime

from purchases.forms import AddManufacturerForm


# Create your views here.
def home(request):
    return HttpResponse("Hello, Django!")

def add_manufacturer(request):
    form = AddManufacturerForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            manufacturer = form.save(commit=False)
            manufacturer.created_date = datetime.now()
            manufacturer.save()
            return redirect("home")
    else:
        return render(request, "purchases/add_manufacturer.html", {"form": form})
