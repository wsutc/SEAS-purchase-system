# from urllib.parse import urlencode
from decimal import Decimal
from http.client import HTTPResponse

from django.contrib import messages
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse

# from setup_sheets.models import PartRevision
from django.utils.text import slugify
from django.views.generic import ListView, View
from django.views.generic.list import MultipleObjectMixin

# from django_listview_filters.filters import (
#     # PAGE_VAR,
#     # ERROR_VAR,
#     # IGNORED_PARAMS,
#     ListViewFilter,
#     # FieldListViewFilter,
# )
from django_listview_filters.mixins import FilterViewMixin

# from django import apps
from furl import furl

# from django.core.exceptions import FieldError, ImproperlyConfigured, ValidationError
# from django.db import models
# from django.db.models import Count, Max, Min
# from django.apps import apps
# from purchases.exceptions import Error, StatusCodeNotFound

# from purchases.models.models_apis import Tracker
# from django.contrib.auth.models import User
# from django.db.models import QuerySet, Field
# from django.contrib.admin.utils import (
#     # get_model_from_relation,
#     get_fields_from_path,
#     # prepare_lookup_value,
#     # reverse_field_path,
#     # lookup_spawns_duplicates,
# )

# from purchases.models.models_data import (
#     PurchaseRequest,
#     Requisitioner,
#     status_code,
#     status_reverse,
# )
# from purchases.models.models_metadata import Carrier  # , Vendor


# from setup_sheets.models import Part
# from web_project import settings

# from web_project.filters import (
#     PAGE_VAR,
#     ERROR_VAR,
#     IGNORED_PARAMS,
#     ListViewFilter,
#     FieldListViewFilter,
# )


def paginate(view: ListView, **kwargs) -> tuple[bool, HTTPResponse]:
    """Validate incoming page number and create redirect if outside bounds or invalid

    Arguments:\n
    view -- a ListView with a paginator defined

    Returns:
    A tuple with a boolean describing whether the URL is changed/needs to redirect and
    the url to redirect to, if required.
    e.g. (True,redirect('home'))
    """
    paginator = view.get_paginator(
        view.queryset, view.paginate_by, view.paginate_orphans
    )

    page = view.request.GET.get("page", None)

    if not page:
        return (False, redirect(view.request.get_full_path()))

    fragment = furl(view.request.get_full_path())
    new_fragment = fragment.copy()

    try:
        page_new = paginator.get_page(page)
    except Exception as err:
        messages.error(view.request, message=f"unable to get page; {err}")
        return (True, redirect(new_fragment.path))

    try:
        page_new_str = str(page_new.number)
        if page != page_new_str:
            # new.remove()
            new_fragment.args["page"] = page_new_str

            messages.info(
                view.request,
                "Page '{og}' not valid, changed to '{new}.'".format(
                    og=page, new=page_new.number
                ),
            )
            return (True, redirect(new_fragment.url))
        else:
            messages.debug(view.request, f"Page '{page}' was valid; no change made.")
            return (False, redirect(new_fragment.url))
    except Exception:
        messages.warning(
            view.request, message="Warning: Error trying to fix page number."
        )
        # new = path.copy()
        return (True, redirect(new_fragment.path))


def redirect_to_next(request: HttpRequest, default_redirect, **kwargs) -> HTTPResponse:
    """Allows for intermediate pages to redirect to the page indicated by the 'next' parameter of the request.

    Especially useful for update and delete views.
    """
    fragment = furl(request.get_full_path())
    if next := fragment.args.get("next", None):
        return next
    else:
        if "slug" in kwargs:
            redirect_url = reverse(
                default_redirect, kwargs={"slug": kwargs.get("slug")}
            )
        else:
            redirect_url = reverse(default_redirect)

        return redirect_url


def get_new_page_fragment(view: ListView, new_page: int) -> str:
    """A helper that replaces the 'page' parameter of a path with <new_path>.

    Useful for defining context for pagination links when using other parameters in a list view.
    """
    request_path = furl(view.request.get_full_path())
    new_path = request_path.copy()
    new_path.args["page"] = new_page

    return new_path.url


def get_app_name(request: HttpRequest):
    func_path = request.resolver_match._func_path
    func_path_split = func_path.split(".", 1)
    return func_path_split[0]


def truncate_string(input: str, num_char: int, postfix: str = "..."):
    if len(input) > num_char:
        string_length = num_char - len(postfix)
        new_string = input[:string_length]
        while new_string[-1:].isspace():
            new_string = new_string[:-1]
        return f"{new_string}{postfix}"
    else:
        return input


class PaginatedListMixin(FilterViewMixin, MultipleObjectMixin, View):
    paginate_by = "20"
    paginate_orphans = "2"
    list_filter = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_obj = context["page_obj"]
        if page_obj.has_previous():
            previous_page = page_obj.previous_page_number()
            context["previous_page_fragment"] = get_new_page_fragment(
                self, previous_page
            )
        if page_obj.has_next():
            next_page = page_obj.next_page_number()
            context["next_page_fragment"] = get_new_page_fragment(self, next_page)
        simple_page_list = context["paginator"].get_elided_page_range(
            context["page_obj"].number, on_each_side=2, on_ends=1
        )

        page_fragments = []
        for page in simple_page_list:
            if page != "...":
                fragment = (page, get_new_page_fragment(self, page))
                page_fragments.append(fragment)
            else:
                page_fragments.append(page, "")

        context["page_list"] = page_fragments

        fragment = furl(self.request.get_full_path())

        return context


def first_true(iterable, default=False, pred=None):
    """Returns the first true value in the iterable.

    If no true value is found, returns *default*

    If *pred* is not None, returns the first item
    for which pred(item) is true.

    """
    # first_true([a,b,c], x) --> a or b or c or x
    # first_true([a,b], x, f) --> a if f(a) else b if f(b) else x
    return next(filter(pred, iterable), default)


def max_decimal_places(numbers: list[float]) -> int:
    def get_decimal_length(num):
        parts = f"{float(num)}".split(".")
        return len(parts[1]) if len(parts) > 1 else 0

    string_values = (get_decimal_length(x) for x in numbers)

    try:
        return max(string_values)
    except ValueError:
        return 0


class Percent:
    def __init__(
        self,
        dec: Decimal,
        decimal_places: int = None,
    ):
        self.per_hundred = Decimal(str(dec)) * Decimal("100")
        self.per_one = dec
        self.has_decimal_places = False
        if decimal_places:
            self.per_hundred = round(self.per_hundred, decimal_places)
            self.per_one = round(self.per_one, decimal_places + 2)
            self.decimal_places = decimal_places
            self.has_decimal_places = True

    @classmethod
    def fromform(cls, val: Decimal, decimal_places: int = None):
        dec = Decimal(str(val)) * Decimal(".01")
        return cls(dec, decimal_places)

    def __mul__(self, other):
        return self.per_one * other

    def __str__(self):
        value = self.per_hundred
        return str(value)
