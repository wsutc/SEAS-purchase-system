from django.http import HttpRequest
from django.urls import reverse
from django import apps
from furl import furl
from django.views.generic import ListView
from http.client import HTTPResponse
from django.contrib import messages
from django.shortcuts import redirect
from django.core.exceptions import FieldError
from django.db import models
from purchases.models.models_apis import Tracker

from purchases.models.models_data import PurchaseRequest, Requisitioner, status_reverse
from purchases.models.models_metadata import Carrier, Vendor

def paginate(view:ListView,**kwargs) -> tuple[bool,HTTPResponse]:
    """Validate incoming page number and create redirect if outside bounds or invalid

    Arguments:\n
    view -- a ListView with a paginator defined

    Returns:
    A tuple with a boolean describing whether the URL is changed/needs to redirect and
    the url to redirect to, if required.
    e.g. (True,redirect('home'))
    """
    paginator = view.get_paginator(view.queryset,view.paginate_by,view.paginate_orphans)

    page = view.request.GET.get('page',None)

    if not page:
        return (False, redirect(view.request.get_full_path()))

    fragment = furl(view.request.get_full_path())
    new_fragment = fragment.copy()

    try:
        page_new = paginator.get_page(page)
    except Exception as err:
        messages.error(view.request,message='unable to get page; {}'.format(err))
        return (True,redirect(new_fragment.path))

    try:
        page_new_str = str(page_new.number)
        if page != page_new_str:
            # new.remove()
            new_fragment.args['page'] = page_new_str

            messages.info(view.request, "Page '{og}' not valid, changed to '{new}.'".format(og=page,new=page_new.number))
            return (True,redirect(new_fragment.url))
        else:
            messages.debug(view.request, "Page '{og}' was valid; no change made.".format(og=page))
            return (False,redirect(new_fragment.url))
    except:
        messages.warning(view.request,message='Warning: Error trying to fix page number.')
        # new = path.copy()
        return (True,redirect(new_fragment.path))

def redirect_to_next(request:HttpRequest, default_redirect, **kwargs) -> HTTPResponse:
    """Allows for intermediate pages to redirect to the page indicated by the 'next' parameter of the request.
    
    Especially useful for update and delete views.
    """
    fragment = furl(request.get_full_path())
    if next := fragment.args.get('next',None):
        return next
    else:
        if 'slug' in kwargs:
            redirect_url = reverse(default_redirect, kwargs = {'slug': kwargs.get('slug')})
        else:
            redirect_url = reverse(default_redirect)

        return redirect_url

def get_new_page_fragment(view:ListView, new_page:int) -> str:
    """A helper that replaces the 'page' parameter of a path with <new_path>.
    
    Useful for defining context for pagination links when using other parameters in a list view.
    """
    request_path = furl(view.request.get_full_path())
    new_path = request_path.copy()
    new_path.args['page'] = new_page

    return new_path.url

def fragment_filters(request:HttpRequest, queryset):
    fragment = furl(request.get_full_path())
    # PurchaseRequestModel = apps.get_model("PurchaseRequest")

    if 'status' in fragment.args:
        key, _ = status_reverse(fragment.args['status'])

        try:
            queryset = queryset.filter(status=key)
        except FieldError:
            purchase_request_qs = PurchaseRequest.objects.filter(status=key)
            queryset = queryset.filter(purchase_request__in=purchase_request_qs)
        except Exception as err:
            messages.error(request, "Exception: {}".format(err))


    if 'vendor' in fragment.args:
        slug = fragment.args['vendor']
        # VendorModel = apps.get_model("Vendor")
        vendor = Vendor.objects.filter(slug=slug)
        if vendor.exists():
            try:
                queryset = queryset.filter(vendor=vendor.first())
            except FieldError:
                purchase_request_qs = PurchaseRequest.objects.filter(vendor=vendor.first())
                queryset = queryset.filter(purchase_request__in=purchase_request_qs)
            except Exception as err:
                messages.error(request, "Exception: {}".format(err))
        else:
            messages.warning(request,"'vendor={}' not found, check that it is typed correctly in address bar.".format(slug))

    if 'sort-by' in fragment.args:
        sort_by = fragment.args['sort-by']
        try:
            queryset = queryset.order_by(sort_by)
        except:
            messages.error(request,"Cannot sort by '{}'. Sort ignored.".format(sort_by))

    if 'requisitioner' in fragment.args:
        slug = fragment.args['requisitioner']

        # queryset = queryset_builder(slug, 'requisitioner', 'purchase_request', Requisitioner, PurchaseRequest, queryset)

        # requisitioner_model = apps.get_model("Requisitioner")
        requisitioner = Requisitioner.objects.filter(slug=slug)
        if requisitioner.exists():
            try:
                queryset = queryset.filter(requisitioner=requisitioner.first())
            except FieldError:
                purchase_request_qs = PurchaseRequest.objects.filter(requisitioner=requisitioner.first())
                queryset = queryset.filter(purchase_request__in=purchase_request_qs)
            except Exception as err:
                messages.error(request, "Exception: {}".format(err))
        else:
            messages.warning(request,"'requisitioner={}' not found, check that it is typed correctly in address bar.".format(slug))

    if 'purchase-request' in fragment.args:
        slug = fragment.args['purchase-request']
        purchase_request = PurchaseRequest.objects.filter(slug=slug)
        if purchase_request.exists():
            try:
                queryset = queryset.filter(purchase_request=purchase_request.first())
            except Exception as err:
                messages.error(request, "Exception: {}".format(err))

        else:
            messages.warning(request,"'{}={}' not found, check that it is typed correctly in address bar.".format("purchase-request",slug))

    if 'carrier' in fragment.args:
        name = fragment.args['carrier']
        # CarrierModel = apps.get_model("Carrier")
        carrier = Carrier.objects.filter(name=name)
        if carrier.exists():
            try:
                queryset = queryset.filter(carrier=carrier.first())
            except Exception as err:
                messages.error(request, "Exception: {}".format(err))

        else:
            messages.warning(request,"'{}={}' not found, check that it is typed correctly in address bar.".format("purchase-request",name))

    return queryset

# def queryset_builder(slug='ups', filter_field:str='carrier', parent_field:str=, filter_model:models.Model, parent_model:models.Model, queryset):
#     object_qs = filter_model.objects.filter(slug=slug)
#     if object_qs.exists():
#         filter_fields = {filter_field: object_qs.first()}
#         try:
#             queryset = queryset.filter(**filter_fields)
#         except FieldError:
#             parent_qs = parent_model.objects.filter(**filter_fields)
#             # field_name = filter_field + '__in'
#             field_in = {parent_field + '__in': parent_qs}
#             queryset = queryset.filter(**field_in)
#         except Exception as err:
#             raise
    
#     return queryset

# class Filter:
#     def __init__():
#         pass

#     @classmethod
#     def from

def build_filter_list(model:models.Model, parent_model:models.Model, field:str, order_by:str):
    """Builds a list of objects <model> that are used by <parent_model> at least once.
    
    <field> is the related manager. Typically, if the parent model was named 'PurchaseRequest,' this should be 'purchaserequest' as a string.
    """
    # list = []
    parent_qs = parent_model.objects.all()
    filter_kwargs = {field + '__in':parent_qs}
    queryset = model.objects.filter(**filter_kwargs).distinct().order_by(order_by)

    return queryset

# TODO: finish building status filtering sidebar
def build_custom_filter_list(field:str, parent_model:models.Model, order_by:str):
    values = parent_model.objects.all().values_list(field, flat=True).order_by().distinct()
    for dict in values:
        print(dict)
    print(str(values.count()) + " vs. " + str(len(values)))
    return values

# def list_filter_context(path:str )
# requisitioner_tuples = []
#         requisitioners = []
#         vendor_tuples = []
#         vendors = []
#         # purchase_reqeusts = PurchaseRequest.objects.filter(vendor__isnull = False)
#         # for vendor in Vendor.objects.filter(purchase_request__in=purchaserequest_set.all)
#         # TODO: figure out filter for better filter lists?
#         fragment = furl(self.request.get_full_path())

#         non_page_args = []
#         for arg in fragment.args:
#             if arg != 'page':
#                 non_page_args.append(arg)

#         context['non_page_args'] = non_page_args
#         for purchase_request in PurchaseRequest.objects.all():
#             vendor = purchase_request.vendor
#             vendor_fragment = fragment.copy()
#             vendor_fragment.args['vendor'] = vendor.slug
#             if vendor_fragment.args.has_key('page'):
#                 del vendor_fragment.args['page']
#             # vendor_fragment = fragment.copy().add(args={'vendor':vendor.slug})
#             requisitioner = purchase_request.requisitioner
#             requisitioner_fragment = fragment.copy()
#             requisitioner_fragment.args['requisitioner'] = requisitioner.slug
#             if requisitioner_fragment.args.has_key('page'):
#                 del requisitioner_fragment.args['page']
#             # requisitioner_fragment = fragment.copy().add(args={'requisitioner':requisitioner.slug})
#             if vendor not in vendors:
#                 vendors.append(vendor)
#                 vendor_tuples.append((vendor, vendor_fragment.url))
#             if requisitioner not in requisitioners:
#                 requisitioners.append(requisitioner)
#                 requisitioner_tuples.append((requisitioner, requisitioner_fragment.url))

def truncate_string(input:str, num_char:int, postfix:str = '...'):
    if len(input) > num_char:
        string_length = num_char - len(postfix)
        new_string = input[:string_length]
        while new_string[-1:].isspace():
            new_string = new_string[:-1]
        return "{}{}".format(new_string,postfix)
    else:
        return input