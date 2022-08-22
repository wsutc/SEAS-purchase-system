from django.http import HttpRequest
from django.urls import reverse
from furl import furl
from django.views.generic import ListView
from http.client import HTTPResponse
from django.contrib import messages
from django.shortcuts import redirect

from purchases.models.models_data import Requisitioner, status_reverse
from purchases.models.models_metadata import Vendor

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

    if 'status' in fragment.args:
        key, _ = status_reverse(fragment.args['status'])

        queryset = queryset.filter(status=key)

    if 'vendor' in fragment.args:
        slug = fragment.args['vendor']
        vendor = Vendor.objects.filter(slug=slug)
        if vendor.exists():
            queryset = queryset.filter(vendor=vendor.first())
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
        requisitioner = Requisitioner.objects.filter(slug=slug)
        if requisitioner.exists():
            queryset = queryset.filter(requisitioner=requisitioner.first())
        else:
            messages.warning(request,"'requisitioner={}' not found, check that it is typed correctly in address bar.".format(slug))

    return queryset