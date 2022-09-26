from django.urls import path

from .views import AccountDetailView

urlpatterns = [
    path("<slug:slug>/", AccountDetailView.as_view(), name="account_detail"),
]
