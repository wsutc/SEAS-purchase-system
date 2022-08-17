from msilib.schema import ListView
from django.shortcuts import render
from django.views.generic import ListView

from web_project.helpers import paginate
from .models import Holder

# Create your views here.
class HolderListView(ListView):
    context_object_name = 'holders'
    paginate_by = '10'
    paginate_orphans = '2'
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