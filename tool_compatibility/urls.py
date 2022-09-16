from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
    path("tools/holders", views.HolderListView.as_view(), name="holder_list"),
    path("tools/inserts/", views.InsertListView.as_view(), name="insert_list"),
    path(
        "tools/<int:pk>-<slug:slug>/",
        views.ToolDetailView.as_view(),
        name="tool_detail",
    ),
    path(
        "tools/manufacturers/<int:pk>-<slug:slug>/",
        views.ManufacturerDetailView.as_view(),
        name="manufacturer_detail",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
