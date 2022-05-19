from unicodedata import name
from django.urls import path
from purchases import views
from purchases.views import VendorDetailView, VendorListView, ProductListView
from purchases.models import Manufacturer, Product

home_list_view = views.HomeListView.as_view(
    queryset=Manufacturer.objects.order_by()[:5],
    context_object_name="manufacturer_list",
    template_name="purchases/home.html"
)

product_list_view = views.ListView.as_view(
    queryset=Product.objects.order_by(),
    context_object_name="product_list",
    template_name="purchases/product_list"
)

urlpatterns = [
    path("", home_list_view, name="home"),
    path("add-mfg/", views.add_mfg, name="add_mfg"),
    path("add-vendor/", views.add_vendor, name="add_vendor"),
    path("add-product/", views.add_product, name="add_product"),
    # path("product-list/", product_list_view, name="product_list"),
    path("new-purchase-request/", views.new_pr, name="new_pr"),
    path("all-vendors", VendorListView.as_view(), name="all_vendors"),
    path("vendor/<int:pk>-<str:slug>/", VendorDetailView.as_view(), name='vendor_detail'),
    path("all-products", ProductListView.as_view(), name='product_list')
]