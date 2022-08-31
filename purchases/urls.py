from django.urls import path, include
from django.views.generic import RedirectView

# from purchases import views
from purchases.views import (
    AccountDetailView,
    BalancesDetailView,
    BalancesListView,
    LedgersListView,
    PurchaseRequestDeleteView,
    PurchaseRequestListView,
    PurchaseRequestUpdateView,
    RequisitionerCreateView,
    RequisitionerDetailView,
    RequisitionerListView,
    RequisitionerPurchaseRequestListView,
    SimpleProductCopyView,
    SimpleProductListView,
    TrackerCreateView,
    TrackerDeleteView,
    TrackerDetailView,
    TrackerListView,
    VendorCreateView,
    VendorDetailView,
    VendorListView,
    PurchaseRequestDetailView,
    VendorDeleteView,
    PurchaseRequestCreateView,
    VendorUpdateView,
    CustomPurchaseRequestCreateView,
    tracking_webhook,
    update_balance,
    update_tracker,
    update_pr_status,
    generate_pr_pdf,
)
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("", RedirectView.as_view(url="purchases/")),
    path("purchases/", PurchaseRequestListView.as_view(), name="home"),
    path(
        "purchases/purchase-request/",
        RedirectView.as_view(pattern_name="home", permanent=False),
    ),
    path("purchases/new-vendor", VendorCreateView.as_view(), name="add_vendor"),
    path("purchases/all-vendors", VendorListView.as_view(), name="all_vendors"),
    path(
        "purchases/vendor/<int:pk>-<str:slug>/",
        VendorDetailView.as_view(),
        name="vendor_detail",
    ),
    path(
        "purchases/vendor/<int:pk>-<str:slug>/update",
        VendorUpdateView.as_view(),
        name="update_vendor",
    ),
    path(
        "purchases/vendor/<int:pk>-<str:slug>/delete",
        VendorDeleteView.as_view(),
        name="delete_vendor",
    ),
    # path("purchases/vendor/modal-new/", VendorModalCreateView.as_view(), name="modal_create_vendor"),
    path(
        "purchases/purchase-request/new/",
        PurchaseRequestCreateView.as_view(),
        name="new_pr",
    ),
    path(
        "purchases/purchase-request/new-custom/",
        CustomPurchaseRequestCreateView.as_view(),
        name="custom_new_pr",
    ),
    path(
        "purchases/purchase-request/<slug:slug>",
        PurchaseRequestDetailView.as_view(),
        name="purchaserequest_detail",
    ),
    path(
        "purchases/purchase-request/<slug:slug>/update",
        PurchaseRequestUpdateView.as_view(),
        name="update_pr",
    ),
    path(
        "purchases/purchase-request/<slug:slug>/update-status",
        update_pr_status,
        name="update_pr_status",
    ),
    path(
        "purchases/purchase-request/<slug:slug>/delete",
        PurchaseRequestDeleteView.as_view(),
        name="delete_pr",
    ),
    path(
        "purchases/purchase-request/<slug:slug>/pdf",
        generate_pr_pdf,
        name="generate_pdf",
    ),
    path("webhooks/tracking/BJD3ZX4b1gNvcIAOhGeTiE6kcC0ugjp/", tracking_webhook),
    path("purchases/trackers/", TrackerListView.as_view(), name="tracker_list"),
    path("purchases/trackers/new/", TrackerCreateView.as_view(), name="create_tracker"),
    path(
        "purchases/trackers/<slug:pk>/",
        TrackerDetailView.as_view(),
        name="tracker_detail",
    ),
    path(
        "purchases/trackers/<slug:pk>/update-tracker/",
        update_tracker,
        name="update_tracker",
    ),
    path(
        "purchases/trackers/<slug:pk>/delete/",
        TrackerDeleteView.as_view(),
        name="tracker_delete",
    ),
    path(
        "purchases/accounts/<int:pk>/",
        AccountDetailView.as_view(),
        name="accounts_detail",
    ),
    path(
        "purchases/purchases/account-transactions/<int:pk>/",
        LedgersListView.as_view(),
        name="ledger_list",
    ),
    path(
        "purchases/account-balances/", BalancesListView.as_view(), name="balances_list"
    ),
    path(
        "purchases/account-balances/<int:pk>/",
        BalancesDetailView.as_view(),
        name="balances_detail",
    ),
    path("purchases/account/<int:pk>/update/", update_balance, name="update_balance"),
    path(
        "purchases/all-requisitioners",
        RequisitionerListView.as_view(),
        name="all_requisitioners",
    ),
    path(
        "purchases/requisitioner/new",
        RequisitionerCreateView.as_view(),
        name="new_requisitioner",
    ),
    path(
        "purchases/requisitioner/<int:pk>-<slug:slug>/",
        RequisitionerDetailView.as_view(),
        name="requisitioner_detail",
    ),
    path(
        "purchases/simple-products/copy/<int:pk>",
        SimpleProductCopyView.as_view(),
        name="copy_simpleproduct",
    ),
    path(
        "purchases/simple-products/",
        SimpleProductListView.as_view(),
        name="simpleproducts",
    ),
    path("purchases/select2/", include("django_select2.urls")),
    path(
        "purchases/<requisitioner>/",
        RequisitionerPurchaseRequestListView.as_view(),
        name="req_filtered_pr",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
