from unicodedata import name
from django.urls import path
from purchases import views
from .views import SetupSheetCreateView, SetupSheetDetailView
from .models import SetupSheet

urlpatterns = [
    path("setup-sheet/<int:pk>-<str:slug>", SetupSheetDetailView.as_view(), name="setup_sheet_detail_view"),
    path("create-setup-sheet", SetupSheetCreateView.as_view(), name="create_new_setup_sheet")
]