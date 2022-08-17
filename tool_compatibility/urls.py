from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("tools/holders", views.HolderListView.as_view(), name="holder_list"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)