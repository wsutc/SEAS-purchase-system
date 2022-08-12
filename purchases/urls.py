from django.urls import path,include
from purchases import views
from purchases.views import (
    BalancesDetailView, BalancesListView, LedgersListView, PurchaseRequestDeleteView,
    PurchaseRequestListView, PurchaseRequestUpdateView, RequisitionerCreateView,
    RequisitionerDetailView, RequisitionerListView, SimpleProductCopyView,
    SimpleProductListView, TrackerCreateView, TrackerDeleteView, TrackerDetailView, TrackerListView, VendorCreateView,
    VendorDetailView, VendorListView, PurchaseRequestDetailView, VendorDeleteView,
    PurchaseRequestCreateView, VendorUpdateView, tracking_webhook
)
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("", PurchaseRequestListView.as_view(), name="home"),
    path("new-vendor", VendorCreateView.as_view(), name='add_vendor'),
    path("all-vendors", VendorListView.as_view(), name="all_vendors"),
    path("vendor/<int:pk>-<str:slug>/", VendorDetailView.as_view(), name='vendor_detail'),
    path("vendor/<int:pk>-<str:slug>/update", VendorUpdateView.as_view(), name='update_vendor'),
    path("vendor/<int:pk>-<str:slug>/delete", VendorDeleteView.as_view(), name='delete_vendor'),
    # path("vendor/modal-new/", VendorModalCreateView.as_view(), name="modal_create_vendor"),
    path("new-purchase-request/", PurchaseRequestCreateView.as_view(), name="new_pr"),
    path("purchase-request/<slug:slug>", PurchaseRequestDetailView.as_view(), name="purchaserequest_detail"),
    path("purchase-request/<slug:slug>/update", PurchaseRequestUpdateView.as_view(), name="update_pr"),
    path("purchase-request/<slug:slug>/update-status", views.update_pr_status, name="update_pr_status"),
    path("purchase-request/<slug:slug>/delete", PurchaseRequestDeleteView.as_view(), name="delete_pr"),
    path("purchase-request/<slug:slug>/pdf", views.generate_pr_pdf, name="generate_pdf"),
    path("webhooks/tracking/BJD3ZX4b1gNvcIAOhGeTiE6kcC0ugjp/",tracking_webhook),
    path("trackers/", TrackerListView.as_view(), name="tracker_list"),
    path("trackers/new/", TrackerCreateView.as_view(), name="create_tracker"),
    path("trackers/<slug:pk>/", TrackerDetailView.as_view(), name="tracker_detail"),
    path("trackers/<slug:pk>/update-tracker/", views.update_tracker, name="update_tracker"),
    path("trackers/<slug:pk>/delete/", TrackerDeleteView.as_view(), name="tracker_delete"),
    path("account-transactions/<int:pk>/", LedgersListView.as_view(), name="ledger_list"), 
    path("account-balances/", BalancesListView.as_view(), name="balances_list"),
    path("account-balances/<int:pk>/", BalancesDetailView.as_view(), name="balances_detail"),
    path("account/<int:pk>/update/", views.update_balance, name="update_balance"),
    path("all-requisitioners", RequisitionerListView.as_view(), name="all_requisitioners"),
    path("requisitioner/new", RequisitionerCreateView.as_view(), name="new_requisitioner"),
    path("requisitioner/<int:pk>-<slug:slug>/", RequisitionerDetailView.as_view(), name="requisitioner_detail"),
    path("simple-products/copy/<int:pk>", SimpleProductCopyView.as_view(), name="copy_simpleproduct"),
    path("simple-products/", SimpleProductListView.as_view(), name="simpleproducts"),
    path("select2/", include("django_select2.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)