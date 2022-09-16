from django.forms import formset_factory
from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView

# from purchases.forms import NewPRIForm
from .models import Item


# Create your views here.
class ItemCreateView(CreateView):
    model = Item
    # template_name = "item_form.html"
    fields = "__all__"


class ItemDetailView(DetailView):
    model = Item


class ItemListView(ListView):
    model = Item


# def manage_items(request):
#     ItemFormSet = formset_factory(NewPRIForm)
#     if request.method == 'POST':
#         formset = ItemFormSet(request.POST, request.FILES)
#         if formset.is_valid():

#             pass
#         else:
#             formset = ItemFormSet()
#         return render(request, 'new_pr.html', {'formset': formset})
