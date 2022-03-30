from django.urls import path
from purchases import views
from purchases.models import Manufacturer

home_list_view = views.HomeListView.as_view(
    queryset=Manufacturer.objects.order_by()[:5],
    context_object_name="manufacturer_list",
    template_name="purchases/home.html"
)

urlpatterns = [
    path("", home_list_view, name="home"),
    path("add-mfg/", views.add_mfg, name="add_mfg"),
    path("add-vendor/", views.add_vendor, name="add_vendor"),
    path("add-product/", views.add_product, name="add_product")
]