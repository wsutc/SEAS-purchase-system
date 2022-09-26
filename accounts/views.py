from django.shortcuts import render
from django.views.generic import DetailView

from .models import Account


# Create your views here.
class AccountDetailView(DetailView):
    model = Account
    template_name = "accounts/account_detail_simple.html"
