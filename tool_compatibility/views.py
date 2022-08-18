# from django.shortcuts import render
from django.views.generic import ListView, View
from django.views.generic.detail import DetailView
from django.views.generic.list import MultipleObjectMixin

from .models import Insert, Tool, Holder, Manufacturer

from web_project.helpers import paginate

# Create your views here.
class PaginatedListMixin(MultipleObjectMixin, View):
    paginate_by = '10'
    paginate_orphans = '2'

    def get(self, request, *args, **kwargs):
        self.queryset = self.get_queryset()

        changed,url = paginate(self)      

        if changed:
            return url
        else:
            return super().get(request, *args, **kwargs) 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_list'] = context['paginator'].get_elided_page_range(context['page_obj'].number,on_each_side=2,on_ends=1)

        return context

class HolderListView(ListView):
    context_object_name = 'holders'
    queryset = Holder.objects.order_by('-created_date')

    # def get_queryset(self):
    #     requisitioner_value = self.request.GET.get('requisitioner', '')
    #     if requisitioner_value != '':
    #         requisitioner = get_object_or_404(Requisitioner,slug=requisitioner_value)
    #         qs = PurchaseRequest.objects.filter(requisitioner = requisitioner).order_by('-created_date')
    #         return qs
    #     else:
    #         # qs = PurchaseRequest.objects.order_by('-created_date')
    #         return self.queryset

class InsertListView(ListView):
    context_object_name = 'insert'
    queryset = Insert.objects.order_by('-created_date')

class ToolDetailView(DetailView):
    model = Tool
    query_pk_and_slug = True

class ManufacturerDetailView(DetailView):
    model = Manufacturer
    query_pk_and_slug = True