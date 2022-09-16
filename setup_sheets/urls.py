from unicodedata import name

from django.urls import path

# from purchases import views
from .views import (
    PartCreateView,
    PartDetailView,
    PartListView,
    PartRevisionCreateView,
    PartRevisionDeleteView,
    SetupSheetCreateView,
    SetupSheetDetailView,
    SetupSheetListView,
)

# from .models import SetupSheet

urlpatterns = [
    path("parts/<int:pk>-<str:slug>", PartDetailView.as_view(), name="part_detail"),
    path("parts/new/", PartCreateView.as_view(), name="create_part"),
    path("parts/", PartListView.as_view(), name="list_part"),
    path(
        "parts/<int:pk>-<str:slug>/add-revision/",
        PartRevisionCreateView.as_view(),
        name="create_partrevision",
    ),
    path(
        "parts/<int:pk>-<str:slug>/<str:revision>/delete/",
        PartRevisionDeleteView.as_view(),
        name="delete_partrevision",
    ),
    path(
        "setup-sheets/<int:pk>-<str:slug>/",
        SetupSheetDetailView.as_view(),
        name="setup_sheet_detail_view",
    ),
    path(
        "setup-sheets/new/",
        SetupSheetCreateView.as_view(),
        name="create_new_setup_sheet",
    ),
    path("setup-sheets/", SetupSheetListView.as_view(), name="list_setupsheet"),
]
