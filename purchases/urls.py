from unicodedata import name
from django.urls import path
from purchases import views
from purchases.views import (
    BalancesDetailView, BalancesListView, LedgersDetailView, LedgersListView, PurchaseRequestListView, PurchaseRequestUpdateView,
    VendorDetailView, VendorListView, PurchaseRequestDetailView,
    PurchaseRequestCreateView, tracking_webhook
)
from purchases.models.models_metadata import Manufacturer, Product
from django.conf.urls.static import static
from django.conf import settings

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
    path("", PurchaseRequestListView.as_view(), name="home"),
    # path("add-mfg/", views.add_mfg, name="add_mfg"),
    path("add-vendor/", views.add_vendor, name="add_vendor"),
    # path("add-product/", views.productcreateview.)
    # path("add-product/", views.add_product, name="add_product"),
    # path("product-list/", product_list_view, name="product_list"),
    # path("new-purchase-request/", PurchaseRequestCreateView.as_view(), name="create_purchase_request"),
    path("new-purchase-request/", PurchaseRequestCreateView.as_view(), name="new_pr"),
    path("all-vendors", VendorListView.as_view(), name="all_vendors"),
    path("vendor/<int:pk>-<str:slug>/", VendorDetailView.as_view(), name='vendor_detail'),
    # path("all-products", ProductListView.as_view(), name='product_list'),
    # path("product/<int:pk>-<str:slug>/", ProductDetailView.as_view(), name='product_detail'),
    # path("all-manufacturers", ManufacturerListView.as_view(), name="all_manufacturers"),
    # path("manufacturer/<int:pk>-<str:slug>/", ManufacturerDetailView.as_view(), name="manufacturer_detail"),
    path("purchase-request/<slug:slug>", PurchaseRequestDetailView.as_view(), name="purchaserequest_detail"),
    # path("purchase-order/<slug:slug>", PurchaseOrderDetailView.as_view(), name="purchaseorder_detail"),
    # path("new-pr-item/<str:pk>", PurchaseRequestItemCreateView.as_view(), name="new_pr_item"),
    # path("manage-products", views.manage_products, name="manage_products"),
    path("update-purchase-request/<slug:slug>", PurchaseRequestUpdateView.as_view(), name="update_pr"),
    # path("update-product/<int:pk>-<str:slug>", ProductUpdateView.as_view(), name="update_product"),
    path("webhooks/tracking/BJD3ZX4b1gNvcIAOhGeTiE6kcC0ugjp/",tracking_webhook),
    path("purchase-request/<slug:slug>/pdf", views.generate_pr_pdf, name="generate_pdf"),
    # path("add-ledger-item/", LedgersCreateView.as_view(), name="add_ledger_item"),
    path("account-transactions/<int:pk>/", LedgersListView.as_view(), name="ledger_list"),
    # path("update-ledger-item/<int:pk>/", LedgersUpdateView.as_view(), name="update_ledger_items"),
    # path("ledger-item/<int:pk>/", LedgersDetailView.as_view(), name="ledger_item"), 
    path("account-balances/", BalancesListView.as_view(), name="balances_list"),
    path("account-balances/<int:pk>/", BalancesDetailView.as_view(), name="balances_detail"),
    path("account/<int:pk>/update/", views.update_balance, name="update_balance"),
    # path("new-purchase-request/add-item/", views.ItemCreateView.as_view(), name="add_item_modal")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)