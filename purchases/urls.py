from unicodedata import name
from django.urls import path,include
from purchases import views
from purchases.views import (
    BalancesDetailView, BalancesListView, LedgersDetailView, LedgersListView, PurchaseRequestDeleteView, PurchaseRequestListView, PurchaseRequestUpdateView, VendorCreateView, VendorModalCreateView,
    VendorDetailView, VendorListView, PurchaseRequestDetailView, VendorDeleteView,
    PurchaseRequestCreateView, VendorUpdateView, tracking_webhook
)
from purchases.models.models_metadata import Manufacturer, Product
from django.conf.urls.static import static
from django.conf import settings

# home_list_view = views.HomeListView.as_view(
#     queryset=Manufacturer.objects.order_by()[:5],
#     context_object_name="manufacturer_list",
#     template_name="purchases/home.html"
# )

# product_list_view = views.ListView.as_view(
#     queryset=Product.objects.order_by(),
#     context_object_name="product_list",
#     template_name="purchases/product_list"
# )

urlpatterns = [
    path("", PurchaseRequestListView.as_view(), name="home"),
    # path("add-vendor/", views.add_vendor, name="add_vendor"),
    path("new-vendor", VendorCreateView.as_view(), name='add_vendor'),
    path("all-vendors", VendorListView.as_view(), name="all_vendors"),
    path("vendor/<int:pk>-<str:slug>/", VendorDetailView.as_view(), name='vendor_detail'),
    path("vendor/<int:pk>-<str:slug>/update", VendorUpdateView.as_view(), name='update_vendor'),
    path("vendor/<int:pk>-<str:slug>/delete", VendorDeleteView.as_view(), name='delete_vendor'),
    path("vendor/modal-new/", VendorModalCreateView.as_view(), name="modal_create_vendor"),
    path("new-purchase-request/", PurchaseRequestCreateView.as_view(), name="new_pr"),
    path("purchase-request/<slug:slug>", PurchaseRequestDetailView.as_view(), name="purchaserequest_detail"),
    path("purchase-request/<slug:slug>/update", PurchaseRequestUpdateView.as_view(), name="update_pr"),
    path("purchase-request/<slug:slug>/update-status", views.update_pr_status, name="update_pr_status"),
    path("purchase-request/<slug:slug>/delete", PurchaseRequestDeleteView.as_view(), name="delete_pr"),
    path("purchase-request/<slug:slug>/pdf", views.generate_pr_pdf, name="generate_pdf"),
    path("webhooks/tracking/BJD3ZX4b1gNvcIAOhGeTiE6kcC0ugjp/",tracking_webhook),
    path("account-transactions/<int:pk>/", LedgersListView.as_view(), name="ledger_list"), 
    path("account-balances/", BalancesListView.as_view(), name="balances_list"),
    path("account-balances/<int:pk>/", BalancesDetailView.as_view(), name="balances_detail"),
    path("account/<int:pk>/update/", views.update_balance, name="update_balance"),
    # path("list-json/<str:model>/", views.autocomplete_list, name="get_autocomp_list"),
    path("select2/", include("django_select2.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)