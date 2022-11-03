from django.views.generic import ListView

from web_project.helpers import PaginatedListMixin

from .models import Part

# from django_listview_filters.filters import RelatedFieldListViewFilter


# Create your views here.
class PartListView(PaginatedListMixin, ListView):
    model = Part
    template_name = "partnumbers/part_list.html"
    # list_filter = [
    #     ("created_by", RelatedFieldListViewFilter),
    # ]
