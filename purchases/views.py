import os
from http.client import HTTPResponse
import io
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.http import FileResponse, HttpResponse, HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from purchases.tracking import get_generated_signature, update_tracking_details
from .models.models_metadata import (
    Carrier, Vendor
)
from .models.models_data import (
    Balance, SimpleProduct, Transaction, PurchaseRequest, Requisitioner
)
from .models.models_apis import (
    Tracker, TrackingWebhookMessage, update_tracker_fields
)
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin
from .forms import (
    CreateUserForm, PurchaseRequestAccountsFormset,
    SimpleProductCopyForm, SimpleProductFormset, TrackerForm#, VendorModelForm
)
from django.contrib import messages

import datetime as dt
import json
from django.utils import timezone

from django.db.transaction import atomic, non_atomic_requests
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm, inch
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, PageTemplate
from reportlab.platypus.paragraph import Paragraph
from reportlab.platypus.frames import Frame
from functools import partial

# from fdfgen import forge_fdf

# from bootstrap_modal_forms.generic import BSModalCreateView

from .forms import AddVendorForm, NewPRForm


# Create your views here.

class VendorListView(ListView):
    context_object_name = 'vendors'
    paginate_by = '10'
    paginate_orphans = '2'
    queryset = Vendor.objects.order_by('name')

    def get(self, request, *args, **kwargs):

        changed,url = paginate(self,'all_vendors')

        if changed:
            return url
        else:
            return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_list'] = context['paginator'].get_elided_page_range(context['page_obj'].number,on_each_side=2,on_ends=1)
        return context

class SimpleProductListView(ListView):
    context_object_name = 'simpleproduct'
    paginate_by = '10'
    paginate_orphans = '2'
    queryset = SimpleProduct.objects.order_by('purchase_request__vendor','name')

    def get(self, request, *args, **kwargs):

        changed,url = paginate(self,'simpleproducts')

        if changed:
            return url
        else:
            return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_list'] = context['paginator'].get_elided_page_range(context['page_obj'].number,on_each_side=2,on_ends=1)
        return context

def paginate(self:ListView,url:str) -> tuple[bool,HTTPResponse]:
    """Validate incoming page number and create redirect if outside bounds or invalid

    Arguments:\n
    self -- a ListView with a paginator defined

    url -- the name of a URL defined in urls.py

    Returns:
    A tuple with a boolean describing whether the URL is changed/needs to redirect and
    the url to redirect to, if required.
    e.g. (True,redirect('home'))
    """
    paginator = self.get_paginator(self.queryset,self.paginate_by,self.paginate_orphans)
    try:
        page = self.request.GET['page']
    except:
        return (False,'')

    page_new = paginator.get_page(page)
    try:
        page_int = int(page)
        if page_int != page_new.number:
            redirect_url = reverse_lazy(url) + "?page=" + str(page_new.number)
        else:
            return (False,'')
    except:
        redirect_url = reverse_lazy(url) + "?page=" + str(page_new.number)
    
    return (True,redirect(redirect_url))

class PurchaseRequestListView(ListView):
    context_object_name = 'purchaserequests'
    paginate_by = '10'
    paginate_orphans = '2'
    # queryset = PurchaseRequest.objects.order_by('-created_date')

    def get_queryset(self):
        requisitioner_value = self.request.GET.get('requisitioner', '')
        if requisitioner_value != '':
            requisitioner = get_object_or_404(Requisitioner,slug=requisitioner_value)
            return PurchaseRequest.objects.filter(requisitioner = requisitioner).order_by('-created_date')
        else:
            return PurchaseRequest.objects.order_by('-created_date')

    def get(self, request, *args, **kwargs):

        changed,url = paginate(self,'home')

        if changed:
            return url
        else:
            return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_list'] = context['paginator'].get_elided_page_range(context['page_obj'].number,on_each_side=2,on_ends=1)

        return context

class VendorDetailView(DetailView):
    model = Vendor
    query_pk_and_slug = True

class PurchaseRequestDetailView(DetailView):
    model = PurchaseRequest
    template_name = "purchases/purchaserequest_detail.html"
    context_object_name = 'purchaserequest'
    query_pk_and_slug = True

class RequisitionerCreateView(CreateView):
    form_class = CreateUserForm
    template_name = "purchases/requisitioner_create.html"

    def form_valid(self, form):
        user = form.save()
        user.refresh_from_db()

        user.requisitioner.wsu_id = form.cleaned_data.get('wsu_id')
        user.save()

        return redirect(user.requisitioner)

class RequisitionerDetailView(DetailView):
    model = Requisitioner
    template_name = "purchases/requisitioner_detail.html"
    query_pk_and_slug = True

class RequisitionerListView(ListView):
    context_object_name = 'requisitioners'
    paginate_by = '10'
    paginate_orphans = '2'
    admin_user = User.objects.filter(username='admin').first()
    queryset = Requisitioner.objects.exclude(user=admin_user).order_by('user')

    def get(self, request, *args, **kwargs):

        changed,url = paginate(self,'all_requisitioners')

        if changed:
            return url
        else:
            return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_list'] = context['paginator'].get_elided_page_range(context['page_obj'].number,on_each_side=2,on_ends=1)

        return context

class RequisitionerUpdateView(UpdateView):
    model = Requisitioner
    form_class = CreateUserForm
    template_name = "purchases/requisitioner_create.html"
    query_pk_and_slug = True

class VendorDeleteView(DeleteView):
    model = Vendor
    success_url = reverse_lazy('all_vendors')

    def form_valid(self, *args, **kwargs):
        object = self.get_object()
        object.delete()
        
        redirect_url = redirect_to_next(self, 'all_vendors')

        return redirect(redirect_url)

class VendorCreateView(CreateView):
    form_class = AddVendorForm
    template_name = 'purchases/add_vendor.html'

# class VendorModalCreateView(BSModalCreateView):
#     template_name = 'purchases/vendor_create_modal.html'
#     form_class = VendorModelForm
#     success_message = 'Success: New Vendor created.'

class PurchaseRequestCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'purchases.add_purchaserequest'
    form_class = NewPRForm
    template_name = 'purchases/new_pr.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['purchase_request_items_formset'] = SimpleProductFormset(prefix='items')
        context['purchase_request_accounts_formset'] = PurchaseRequestAccountsFormset(prefix='accounts')
        context['requisitioner'] = Requisitioner.objects.get(user=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        purchase_request_items_formset = SimpleProductFormset(self.request.POST, prefix='items')
        purchase_request_accounts_formset = PurchaseRequestAccountsFormset(self.request.POST, prefix='accounts')
        if not (priValid := purchase_request_items_formset.is_valid()):
            print(purchase_request_items_formset.errors)
        if not (praValid := purchase_request_accounts_formset.is_valid()):
            print(purchase_request_accounts_formset.errors)
        if form.is_valid() and priValid and praValid:
            return self.form_valid(form, purchase_request_items_formset, purchase_request_accounts_formset)
        else:
            return self.form_invalid(form, purchase_request_items_formset, purchase_request_accounts_formset)

    def form_valid(self, form, purchase_request_items_formset, purchase_request_accounts_formset):
        self.object = form.save(commit=False)
        self.object.save()

        ## Add Items
        purchase_request_items = purchase_request_items_formset.save(commit=False)
        for item in purchase_request_items:
            item.purchase_request = self.object
            item.save()
        
        ## Add Accounts
        purchase_request_accounts = purchase_request_accounts_formset.save(commit=False)
        for account in purchase_request_accounts:
            account.purchase_request = self.object
            account.save()

        # # Set PR totals and update balance (balance isn't functional)
        self.object.update_totals()

        return redirect(self.object)

    def form_invalid(self, form, purchase_request_items_formset, purchase_request_accounts_formset):
        return self.render_to_response(
            self.get_context_data(
                form = form,
                purchase_request_items_formset = purchase_request_items_formset,
                purchase_request_accounts_formset = purchase_request_accounts_formset
            )
        )

class PurchaseRequestUpdateView(UpdateView):
    permission_required = 'purchases.change_purchaserequest'
    model = PurchaseRequest
    form_class = NewPRForm
    template_name = "purchases/purchaserequest_update.html"
    query_pk_and_slug = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['purchase_request_items_formset'] = SimpleProductFormset(self.request.POST, instance=self.object, prefix='items')
            context['purchase_request_accounts_formset'] = PurchaseRequestAccountsFormset(self.request.POST, instance=self.object, prefix='accounts')
        else:
            context['purchase_request_items_formset'] = SimpleProductFormset(instance=self.object, prefix='items')
            context['purchase_request_accounts_formset'] = PurchaseRequestAccountsFormset(instance=self.object, prefix='accounts')
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        self.object = form.save(commit=False)
        
        purchase_request_items_formset = context['purchase_request_items_formset']
        purchase_request_accounts_formset = context['purchase_request_accounts_formset']

        if not purchase_request_items_formset.is_valid():
            return self.form_invalid(form)
        if not purchase_request_accounts_formset.is_valid():
            return self.form_invalid(form)
        
        purchase_request_items_formset.save(commit=True)
        purchase_request_accounts_formset.save(commit=True)

        self.object.save()

        self.object.update_totals()

        return redirect(self.object)

    def form_invalid(self, form):
        context = self.get_context_data()
        return self.render_to_response(
            self.get_context_data(
                form=form,
                purchase_request_items_formset=context['purchase_request_items_formset'],
                purchase_request_accounts_formset=context['purchase_request_accounts_formset']
            )
        )

def update_pr_status(request,slug,*args, **kwargs):
    new_status = request.GET['status']

    status_number = ''
    match new_status:
        case 'approved':
            status_number = '2'
        case 'shipped':
            status_number = '7'
        case 'ordered':
            status_number = '6'
        case 'awaiting-approval':
            status_number = '1'
        case 'received':
            status_number = '8'
        case _:
            status_number = None

    if status_number:
        qs = PurchaseRequest.objects.filter(slug=slug)
        count = qs.count()
        if count != 1:
            messages.add_message(request, messages.ERROR, message="Slug returned too many results: {}; no records updated.".format(count))
        else:
            qs.update(status=status_number)
            messages.add_message(request, messages.SUCCESS, message="{}'s status updated to {}.".format(qs.first(), new_status.title().replace('-',' ')))
    else:
        messages.add_message(request,messages.WARNING,message="Chosen status '{}' not valid. Contact admin for help.".format(new_status.title().replace('-',' ')))

    return redirect('purchaserequest_detail', slug = slug)

def redirect_to_next(view, default_redirect='home'):

    next = view.request.GET.get('next',None)
    if next:
        return next
    else:
        redirect_url = reverse_lazy(default_redirect)

        return redirect_url

class PurchaseRequestDeleteView(DeleteView):
    model = PurchaseRequest

    def form_valid(self, *args, **kwargs):
        object = self.get_object()
        object.delete()

        redirect_url = redirect_to_next(self)

        return redirect(redirect_url)

class VendorUpdateView(UpdateView):
    model = Vendor
    form_class = AddVendorForm
    template_name = "purchases/vendor_update.html"
    query_pk_and_slug = True

class VendorDeleteView(DeleteView):
    model = Vendor
    success_url = reverse_lazy('all_vendors')

    def form_valid(self, *args, **kwargs):
        object = self.get_object()
        object.delete()
        
        redirect_url = redirect_to_next(self, 'all_vendors')

        return redirect(redirect_url)

class SimpleProductCopyView(UpdateView):
    model = SimpleProduct
    form_class = SimpleProductCopyForm
    template_name = "purchases/simpleproduct_copy.html"

    def form_valid(self, form) -> HttpResponse:
        object = self.get_object()

        object.purchase_request = form.cleaned_data.get('purchase_request')
        object.quantity = form.cleaned_data.get('quantity')
        object.unit_price = form.cleaned_data.get('unit_price')
        object.name = form.cleaned_data.get('name')

        object.pk = None
        object._state.adding = True
        object.save()
        object.purchase_request.update_totals()

        return redirect(object.purchase_request)

@csrf_exempt
@require_POST
@non_atomic_requests
def tracking_webhook(request):

    if request.method == 'HEAD':
        response = HttpResponse("Message successfully received.", content_type="text/plain")
        return response
    else:
        secret = settings._17TRACK_KEY
        given_token = request.headers.get("sign","")

        if signature := get_generated_signature(request.body,secret) != given_token:
            return HttpResponseForbidden(
                "Inconsistency in response signature.",
                content_type="text/plain"
            )

        TrackingWebhookMessage.objects.filter(
            received_at__lte = timezone.now() - dt.timedelta(days=7)
        ).delete()

        payload = json.loads(request.body)
        TrackingWebhookMessage.objects.create(
            received_at=timezone.now(),
            payload=payload
        )

        process_webhook_payload(payload)

        return HttpResponse("Message successfully received.", content_type="text/plain")

@atomic
def process_webhook_payload(payload):
    event_type = payload.get('event')
    data = payload.get('data')

    tracking_number = data.get('number')
    carrier_code = data.get('carrier')
    status = data['track_info']['latest_status']['status']
    sub_status = data['track_info']['latest_status']['sub_status']
    delivery_estimate = data['track_info']['time_metrics']['estimated_delivery_date']['from']
    last_update_date = data['track_info']['latest_event']['time_utc']
    events = data['track_info']['tracking']['providers'][0]['events']
    events_hash = data['track_info']['tracking']['providers'][0]['events_hash']

    try:
        carrier = Carrier.objects.get(carrier_code=carrier_code)
        tracker, _ = Tracker.objects.get_or_create(tracking_number=tracking_number,carrier=carrier)
    except ObjectDoesNotExist as err:
        return

    if event_type == 'TRACKING_UPDATED':
        fields = {
            'status': status,
            'sub_status': sub_status,
            'delivery_estimate': delivery_estimate,
            'events': events,
            'events_hash': events_hash
        }
        update_tracker_fields(tracker,fields)

    return

def generate_pr_pdf(request,slug):
    purchase_request = PurchaseRequest.objects.get(slug=slug)
    buffer = io.BytesIO()

    def header(canvas:canvas, doc, content):
        """Creates header from flowable?"""
        canvas.saveState()
        w, h = content.wrap(doc.width, doc.topMargin)
        content.drawOn(canvas, doc.leftMargin, doc.height + doc.bottomMargin + doc.topMargin - h)
        canvas.restoreState()

    def footer(canvas:canvas, doc, content):
        """Creates footer from flowable?"""
        canvas.saveState()
        w, h = content.wrap(doc.width, doc.bottomMargin)
        content.drawOn(canvas, doc.leftMargin, h)
        canvas.restoreState()

    def header_and_footer(canvas:canvas, doc, header_content, footer_content):
        """Need to build both header AND footer in same function"""
        header(canvas, doc, header_content)
        footer(canvas, doc, footer_content)

    styles = getSampleStyleSheet()

    styles_title = styles['Title']
    styles_title.name = 'Header-Title'
    styles_title.fontSize = 40
    styles_title.textColor = colors.HexColor("#CA1237")
    
    ## Set header styles
    styles.add(styles_title)

    # style_header_normal = styles['Normal']
    # style_header_title = styles['Title']
    # style_header_title.fontSize = 40

    ## Set footer styles
    # style_footer_normal = styles['Normal']

    filename = purchase_request.number + ".pdf"

    doc = SimpleDocTemplate(buffer, pagesize=letter, title=purchase_request.number)

    doc.leftMargin = doc.rightMargin = 1*cm
    # doc.rightMargin = 42
    doc.width = doc.pagesize[0] - doc.leftMargin - doc.rightMargin

    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')  #, showBoundary=1)

    header_content = Paragraph(purchase_request.number, styles['Header-Title'])
    footer_content = Paragraph("This is a footer", styles['Normal'])

    template = PageTemplate(id='test', frames=frame, onPage=partial(header_and_footer, header_content=header_content, footer_content=footer_content))

    doc.addPageTemplates([template])

    elements = []

    # Define purchase request information table
    info_column_widths = [.9*inch,2.4*inch,.9*inch,2.4*inch]

    # link = '<link href="' + purchase_request.vendor.website + '">' + purchase_request.vendor.website + '</link>'

    # <td rowspan=2>{{ object.vendor.street1 }}<br>
    #                             {% if object.vendor.street2 %}
    #                                 {{ object.vendor.street2 }}<br>
    #                             {% endif %}
    #                             {% if object.vendor.city %}
    #                                 {{ object.vendor.city }}, {{ object.vendor.state.abbreviation }} {{ object.vendor.zip }}
    #                             {% else %}
    #                             {% endif %}
    #                         </td>
    vendor = purchase_request.vendor
    address_line = ''
    if hasattr(vendor.state,'abbreviation'):
        address_line += str(vendor.state.abbreviation)
        if city := vendor.city:
            address_line = str(city) + ', ' + address_line + ' ' + str(vendor.zip)
            if street2 := vendor.street2:
                address_line = str(street2) + '\n' + address_line
            if street1 := vendor.street1:
                address_line = str(street1) + '\n' + address_line

    info_data = [
        [
            'Needed By', purchase_request.need_by_date,
            'Requestor', purchase_request.requisitioner.user.get_full_name()
        ],
        [
            'Vendor', purchase_request.vendor.name,
            'Email', purchase_request.requisitioner.user.email
        ],
        [
            'Address', address_line,
            'Phone', purchase_request.requisitioner.phone
        ],
        [
            '', '',
            'Department', purchase_request.requisitioner.department.code
        ],
        ['Phone', purchase_request.vendor.phone],
        ['Email', purchase_request.vendor.email],
        ['Website', purchase_request.vendor.website]
    ]

    info_table = Table(info_data, info_column_widths)

    info_table.setStyle(
        TableStyle(
            [
                # ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
                # ('ALIGN',(0,0),(-1,0),'CENTER'),
                # ('LINEBELOW',(0,0),(-1,-1),0.5,colors.black),
                # ('FONTNAME',(0,1),(-1,0),'Helvetica'),
                # ('ALIGN',(1,1),(-3,-1),'CENTER'),
                ('ALIGN',(0,0),(0,-1),'RIGHT'),
                ('VALIGN',(0,2),(1,2),'TOP'),
                ('FONTNAME',(0,0),(0,-1),'Helvetica-Bold'),
                ('ALIGN',(2,0),(2,-1),'RIGHT'),
                ('FONTNAME',(2,0),(2,-1),'Helvetica-Bold'),
                ('SPAN',(0,2),(0,3)),
                ('SPAN',(1,2),(1,3)),
                # ('ROWBACKGROUNDS',(0,1),(-1,-5),[colors.aliceblue,colors.white]),
                # ('BOX',(0,0),(-1,-1),0.5,colors.black),
                ('SPAN',(2,4),(-1,-1)),
                # ('INNERGRID',(0,0),(-1,-5),0.1,colors.darkgray),
                # ('BOX',(-3,-4),(-1,-1),0.5,colors.black),
                # ('ALIGN',(-3,-4),(-1,-1),'RIGHT'),
                # ('LINEABOVE',(-3,-1),(-1,-1),0.1,colors.darkgray),
                # ('SPAN',(0,-4),(3,-1)),
                # ('SPAN',(-3,-4),(-2,-4))
            ]
        )
    )

    elements.append(info_table)

    # Define Table
    data = [
            [
            'Description',
            'Identifier',
            'Vendor ID',
            'QTY',
            'Unit',
            'Price',
            'Ext. Price'
            ]
        ]

    ## Create rows for each item
    data = appendAsList(data, item_rows(purchase_request))

    ## Create rows showing subtotal, shipping, tax, and grand total
    total_rows = [
        ['','','','','',   'Subtotal',purchase_request.subtotal],
        ['','','','','',   'Shipping',purchase_request.shipping],
        ['','','','','',        'Tax',purchase_request.sales_tax],
        ['','','','','','Grand Total',purchase_request.grand_total]
    ]

    data = appendAsList(data, total_rows)

    ## Create a 'standardized width' [sw] that is 1% of the doc.width
    sw = doc.width / 100

    ## Use the sw to generate a table that is exactly the same width as doc.width
    column_widths = [38*sw,14*sw,14*sw,7*sw,7*sw,8*sw,12*sw]

    items_table = Table(data,colWidths=column_widths)           # Create table

    ## Set style for table and rows
    items_table.setStyle(
        TableStyle(
            [
                ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
                ('ALIGN',(0,0),(-1,0),'CENTER'),
                ('LINEBELOW',(0,0),(-1,0),0.5,colors.black),
                ('FONTNAME',(0,1),(-1,0),'Helvetica'),
                ('ALIGN',(1,1),(-3,-1),'CENTER'),
                ('ALIGN',(-2,1),(-1,-5),'RIGHT'),
                ('ROWBACKGROUNDS',(0,1),(-1,-5),[colors.aliceblue,colors.white]),
                ('BOX',(0,0),(-1,-5),0.5,colors.black),
                ('INNERGRID',(0,0),(-1,-5),0.1,colors.darkgray),
                # ('BOX',(-3,-4),(-1,-1),0.5,colors.black),
                ('ALIGN',(-3,-4),(-1,-1),'RIGHT'),
                ('LINEABOVE',(-3,-1),(-1,-1),0.1,colors.darkgray),
                # ('SPAN',(0,-4),(3,-1)),
                # ('SPAN',(-3,-4),(-2,-4))
            ]
        )
    )

    ## Add items_table to 'elements' list
    elements.append(items_table)

    doc.build(elements)

    # doc.showPage()
    # doc.save()

    buffer.seek(0)

    return FileResponse(buffer, as_attachment=True, filename=filename)

def get_image(filename:str,url:str):
    """ Get an image for the PDF """
    if not os.path.exists(filename):
        response = HttpResponse()

def appendAsList(data:list[list:str], list:list[list:str]):
    for i in list:
        data.append(i)

    return data

def item_rows(purchase_request:PurchaseRequest):
    """ Create nested list of items to be used in a table """
    items = purchase_request.simpleproduct_set.all()
    rows = []
    for i in items:
        row = [
            i.name,
            i.identifier,
            "",
            i.quantity,
            i.unit,
            i.unit_price,
            i.extended_price
        ]
        rows.append(row)

    return rows

def fill_pr_pdf(request,purchase_request:PurchaseRequest):
    pass

class BalancesListView(ListView):
    model = Balance
    template_name = 'purchases/balances_list.html'

class BalancesDetailView(DetailView):
    model = Balance
    template_name = 'purchases/balances_detail.html'

# class LedgersUpdateView(UpdateView):
#     model = Transaction
#     form_class = LedgersForm
#     template_name = 'purchases/ledgers_create.html'
#     success_url = reverse_lazy('balances_list')

#     # def post(self):
#     #     pass

class LedgersDetailView(DetailView):
    model = Transaction

class LedgersListView(ListView):
    model = Transaction
    template_name = 'purchases/ledgers_list.html'

def update_balance(request, pk:int):
    balance = get_object_or_404(Balance,pk=pk)
    balance.recalculate_balance()

    return redirect('balances_list')

class TrackerListView(ListView):
    context_object_name = 'tracker'
    paginate_by = '10'
    paginate_orphans = '2'
    # queryset = Tracker.objects.order_by('-purchase_request__number','tracking_number')

    def get_queryset(self):
        pr_slug = self.request.GET.get('purchase-request', '')
        if pr_slug:
            purchase_request = get_object_or_404(PurchaseRequest,slug=pr_slug)
            return Tracker.objects.filter(purchase_request=purchase_request).order_by('tracking_number')
        else:
            return Tracker.objects.order_by('-purchase_request__number','tracking_number')

    def get(self, request, *args, **kwargs):

        if not self.queryset:
            self.queryset = self.get_queryset()

        changed,url = paginate(self,'tracker_list')

        if changed:
            return url
        else:
            return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_list'] = context['paginator'].get_elided_page_range(context['page_obj'].number,on_each_side=2,on_ends=1)
        return context

class TrackerCreateView(CreateView):
    form_class = TrackerForm
    template_name = 'purchases/tracker_create.html'

    def post(self, request, *args, **kwargs) -> HTTPResponse:
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    # def form_valid(self, form, purchase_request_items_formset, purchase_request_accounts_formset):
    #     self.object = form.save(commit=False)
    #     self.object.save()

    #     ## Add Items
    #     purchase_request_items = purchase_request_items_formset.save(commit=False)
    #     for item in purchase_request_items:
    #         item.purchase_request = self.object
    #         item.save()
        
    #     ## Add Accounts
    #     purchase_request_accounts = purchase_request_accounts_formset.save(commit=False)
    #     for account in purchase_request_accounts:
    #         account.purchase_request = self.object
    #         account.save()

    #     # # Set PR totals and update balance (balance isn't functional)
    #     self.object.update_totals()

    #     return redirect(self.object)

    # def form_invalid(self, form, purchase_request_items_formset, purchase_request_accounts_formset):
    #     return self.render_to_response(
    #         self.get_context_data(
    #             form = form,
    #             purchase_request_items_formset = purchase_request_items_formset,
    #             purchase_request_accounts_formset = purchase_request_accounts_formset
    #         )
    #     )

class TrackerDetailView(DetailView):
    model = Tracker
    template_name = "purchases/tracker_detail.html"
    query_pk_and_slug = True

def update_tracker(request,pk,*args, **kwargs):
    tracker = get_object_or_404(Tracker, pk=pk)
    response = update_tracking_details(tracker.tracking_number, tracker.carrier.carrier_code)
    
    if response.get('code') == 0:
        status = response.get('status')
        sub_status = response.get('sub_status')
        delivery_estimate = response.get('delivery_estimate')
        events = response.get('events')
        events_hash = response.get('events_hash')

        fields = {
            'status': status,
            'sub_status': sub_status,
            'delivery_estimate': delivery_estimate,
            'events': events,
            'events_hash': events_hash
        }

        update_tracker_fields(tracker,fields)

    return redirect(tracker)