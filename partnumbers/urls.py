from django.urls import path

from partnumbers.views import PartListView

urlpatterns = [
    path("", PartListView.as_view(), name="all-parts"),
]
