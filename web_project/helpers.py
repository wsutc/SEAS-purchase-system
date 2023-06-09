import logging
from decimal import Decimal
from http.client import HTTPResponse
from inspect import getmembers
from pprint import pprint
from types import FunctionType

from django.conf import settings
from django.contrib import admin, messages
from django.contrib.auth.decorators import login_required

# from django.contrib.auth.middleware import AuthenticationMiddleware
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import ListView, View
from django.views.generic.list import MultipleObjectMixin
from django_listview_filters.mixins import FilterViewMixin
from furl import furl

# from silk.profiling.profiler import silk_profile


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
    """Allows for intermediate pages to redirect to the page indicated by the 'next'
    parameter of the request.

    Especially useful for update and delete views.

    :param slug: slug of object to redirect to
    :type slug: string, optional
    :return: response to redirect to
    :rtype: HttpRequest
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

    Useful for defining context for pagination links when using other parameters in a
    list view.
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

        # fragment = furl(self.request.get_full_path())

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


def trim_trailing_zeros(value: (float | Decimal | str)) -> Decimal:
    if isinstance(value, Decimal):
        _, _, exponent = value.as_tuple()
    else:
        _, _, exponent = Decimal(value).as_tuple()

    if exponent < 0:
        new_str = str(value).rstrip("0")
        return Decimal(new_str)
    else:
        return Decimal(value)


def set_zero(value: (float | Decimal | str)) -> Decimal:
    decimal_from_string = Decimal(str(value))

    _, decimal_digits, _ = decimal_from_string.as_tuple()

    if len(decimal_digits) == 1 and decimal_digits[0] == 0:
        return Decimal()
    else:
        return decimal_from_string


def ratio_to_whole(ratio: Decimal) -> Decimal:
    return Decimal(str(ratio)) * Decimal("100")


def whole_to_ratio(whole: Decimal) -> Decimal:
    return Decimal(str(whole)) * Decimal("0.01")


class Percent:
    def __init__(
        self,
        value,
        decimal_places: int = None,
    ):
        new_value = trim_trailing_zeros(value)
        per_hundred_dec = trim_trailing_zeros(ratio_to_whole(value))

        if decimal_places:
            new_value = round(new_value, decimal_places + 2)
            per_hundred_dec = round(per_hundred_dec, decimal_places)
            self.decimal_places = decimal_places
            self.has_decimal_places = True
        else:
            self.decimal_places = None
            self.has_decimal_places = False

        self.value = set_zero(new_value)
        self.per_hundred = set_zero(per_hundred_dec)

    @classmethod
    def fromform(cls, val: Decimal, field_decimal_places: int = None):
        """Create Percent from human-entry (out of 100)"""
        dec = whole_to_ratio(val)
        return cls(dec, decimal_places=field_decimal_places)

    def __mul__(self, other):
        """Multiply using the ratio (out of 1) instead of human-readable out of 100"""
        return self.value.__mul__(other)

    def __float__(self):
        return float(self.value)

    def as_tuple(self):
        dec_tuple = self.value.as_tuple()
        return dec_tuple

    def is_finite(self):
        return self.value.is_finite()

    def __repr__(self) -> str:
        value = f"Percentage('{self.value}', '{self.per_hundred}%')"
        return value

    def __str__(self):
        value = f"{self.per_hundred}%"
        return value


def is_number(s):
    if s is None:
        return False
    try:
        float(s)
        return True
    except ValueError:
        return False


def sort_title(title: str) -> str:
    ARTICLES = {"a", "an", "the"}

    title = title.lower()

    first, _, rest = title.partition(" ")
    rtitle = f"{rest}, {first}" if first in ARTICLES else title

    return rtitle


# -------------------------- Debug tools/helpers ----------------------------------
def plog(
    logger: logging.Logger,
    level: int,
    path: str,
    text: str,
    value: (str | float),
):
    message = f"`{path}` {text}: {value}"
    logger.log(level, message)


def attributes(obj):
    disallowed_names = {
        name for name, value in getmembers(type(obj)) if isinstance(value, FunctionType)
    }
    return {
        name: getattr(obj, name)
        for name in dir(obj)
        if name[0] != "_" and name not in disallowed_names and hasattr(obj, name)
    }


def print_attributes(obj):
    pprint(attributes(obj))


def login_exempt(view):
    view.login_exempt = True
    return view


# ------------------------------ Middlewares -----------------------------------


class LoginRequiredMiddleware:
    # @silk_profile(name="Login Required Middleware")
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        import inspect

        from django.contrib.auth import views as auth_views

        if getattr(view_func, "login_exempt", False):
            return

        if request.user.is_authenticated:
            return

        ALLOWED_ANONYMOUS_VIEWS = settings.ALLOWED_ANONYMOUS_VIEWS
        all_auth_views = inspect.getmembers(auth_views)
        allowed_views = (
            x[1] for x in all_auth_views if x[0] in ALLOWED_ANONYMOUS_VIEWS
        )

        if view_func.view_class in allowed_views:
            """Allow views specified by ALLOWED_ANONYMOUS_VIEWS to be viewed even if not
            authenticated.
            """
            return

        return login_required(view_func)(request, *view_args, **view_kwargs)


def redirect_object_or_next(object, request, next_param="next"):
    """Redirect to specified 'next' page or object's detail page.

    :param object: Object/model to be redirected to if no 'next' page specified
    :type object: Django models.Model object
    :param request: The request as specified by the server
    :type request: HTTPRequest
    :param next_param: Paramater used in URL to specify 'next' page
    :type next_param: str, optional
    """
    next = request.GET.get(next_param, None)
    if next:
        url = next
    else:
        url = object

    return redirect(url)


class AdminResponseMixin(admin.ModelAdmin):
    """A mixin for `admin.ModelAdmin` classes that automatically redirects back to
    object on site as well as back to list if deleted.
    """

    def response_change(self, request, obj, post_url_continue=...):
        return redirect_object_or_next(obj, request)

    def response_delete(self, request, obj, post_url_continue=...):
        return redirect_object_or_next(obj, request)


# def sort_list_by_lower():
#     # TODO: make this more elegant
#     # sort vendor as lower case (python sorts lower different than upper by default)
#     filter_name = "purchase_request__vendor"

#     # django-listview-filters added `get_filter_by_name` in later versions
#     # (should be removed)
#     try:
#         filter = self.get_filter_by_name(filter_name)
#     except Exception:
#         if len(self.filter_specs) > 0:
#             for filter_spec in self.filter_specs:
#                filter = filter_spec if filter_spec.field_path == filter_name else None
#         else:
#             filter = None

#     if filter:
#         filter.lookup_choices = sorted(
#             filter.lookup_choices, key=lambda x: x[1].lower()
#         )
