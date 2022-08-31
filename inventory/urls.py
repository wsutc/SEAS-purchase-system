from unicodedata import name
from django.urls import path

from .views import ItemCreateView, ItemDetailView, ItemListView

urlpatterns = [
    path("new-inventory-item", ItemCreateView.as_view(), name="create_new_item"),
    path(
        "inventory-item/<str:id>-<str:slug>",
        ItemDetailView.as_view(),
        name="item_detail_view",
    ),
    path("inventory-list", ItemListView.as_view(), name="inventory_list"),
]
