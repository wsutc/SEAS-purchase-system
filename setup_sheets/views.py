# from django.shortcuts import render
from audioop import reverse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView,CreateView,ListView,DeleteView
from purchases.views import paginate
from setup_sheets.forms import PartRevisionForm
from setup_sheets.models import Part, SetupSheet, PartRevision
# from django import views,forms

# Create your views here.
class SetupSheetDetailView(DetailView):
    model = SetupSheet
    query_pk_and_slug = True

class SetupSheetCreateView(CreateView):
    model = SetupSheet
    fields = [
        'name',
        'part',
        'part_revision',
        'program_name',
        'operation',
        'size',
        'created_by',
        'revision',
        'revision_date',
        # 'tools',
        'notes'
        ]

    # success_url = reverse('setup_sheet_detail_view')

    # def get_success_url(self):
    #     return reverse_lazy('setup_sheet_detail_view', kwargs={'pk': self.object.pk})

class SetupSheetListView(ListView):
    context_object_name = 'setupsheet'
    paginate_by = '10'
    paginate_orphans = '2'
    queryset = SetupSheet.objects.order_by('operation')

    def get(self, request, *args, **kwargs):

        changed,url = paginate(self,'list_setupsheet')

        if changed:
            return url
        else:
            return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_list'] = context['paginator'].get_elided_page_range(context['page_obj'].number,on_each_side=2,on_ends=1)

        return context

class PartDetailView(DetailView):
    model = Part
    query_pk_and_slug = True

class PartListView(ListView):
    context_object_name = 'part'
    paginate_by = '10'
    paginate_orphans = '2'
    queryset = Part.objects.order_by('number')

    def get(self, request, *args, **kwargs):

        changed,url = paginate(self,'list_part')

        if changed:
            return url
        else:
            return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_list'] = context['paginator'].get_elided_page_range(context['page_obj'].number,on_each_side=2,on_ends=1)

        return context

class PartCreateView(CreateView):
    model = Part
    fields = "__all__"

class PartRevisionCreateView(CreateView):
    # model = PartRevision
    form_class = PartRevisionForm
    template_name = "setup_sheets/partrevision_form.html"
    # fields = "__all__"

    def get_initial(self):
        initial_og = super().get_initial()
        part_obj = get_object_or_404(Part,slug=self.kwargs.get('slug'),pk=self.kwargs.get('pk'))
        initial = initial_og.copy()
        initial['part'] = part_obj.pk
        return initial

    def form_valid(self, form):
        # form = super().form_valid(form)
        self.object = form.save(commit=True)
        # object.part = form.cleaned_data.get('part')
        part = form.cleaned_data.get('part')
        part_obj = Part.objects.get(pk=part.pk)
        return redirect(part_obj)

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     part_obj = get_object_or_404(Part,slug=self.kwargs.get('slug'),pk=self.kwargs.get('pk'))
    #     context['part'] = part_obj
    #     return context

def redirect_to_next(view, default_redirect='home'):

    next = view.request.GET.get('next',None)
    if next:
        return next
    else:
        redirect_url = reverse_lazy(default_redirect)

        return redirect_url

class PartRevisionDeleteView(DeleteView):
    model = PartRevision

    # def get(self, request, *args, **kwargs):
    #     get = super().get(request, *args, **kwargs)
    #     return get

    # def post(self, request, *args, **kwargs):
    #     post = super().post(request, *args, **kwargs)

    #     return post

    def get_context_data(self, **kwargs):
        part_obj = get_object_or_404(Part, slug=self.kwargs.get('slug'), pk=self.kwargs.get('pk'))
        self.object = get_object_or_404(PartRevision, part=part_obj, revision=self.kwargs.get('revision'))
        kwargs['object'] = self.object
        context = super().get_context_data(**kwargs)
        # context['partrevision'] = context['object']
        # context['view']['object']
        return context

    def form_valid(self, *args, **kwargs):
        part_obj = get_object_or_404(Part, slug=self.kwargs.get('slug'), pk=self.kwargs.get('pk'))
        object = get_object_or_404(PartRevision, part=part_obj, revision=self.kwargs.get('revision'))
        # object = self.get_object()
        object.delete()

        redirect_url = redirect_to_next(self, 'part_list')

        return redirect(redirect_url)