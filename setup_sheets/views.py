# from django.shortcuts import render
from audioop import reverse
from django.views.generic import DetailView,CreateView
from setup_sheets.models import SetupSheet
# from django import views,forms

# Create your views here.
class SetupSheetDetailView(DetailView):
    model = SetupSheet
    query_pk_and_slug = True

class SetupSheetCreateView(CreateView):
    model = SetupSheet
    fields = [
        'name',
        'part_number',
        'part_revision',
        'program_name',
        'operation',
        'material',
        'size',
        'created_by',
        'revision',
        'revision_date',
        # 'tools',
        'notes'
        ]

    # success_url = reverse('setup_sheet_detail_view')

    def get_success_url(self):
        return reverse('setup_sheet_detail_view', kwargs={'pk': self.get_context_data()['object_name'].pk})