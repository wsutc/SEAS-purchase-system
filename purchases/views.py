from ast import If
import base64
import hashlib
import hmac
import os
from django.apps import AppConfig,apps
from django.template import RequestContext
from traitlets import default
import urllib3
from http.client import HTTPResponse
import io
from itertools import product
from django.conf import settings
from django.forms import formset_factory
from django.http import FileResponse, HttpResponse, HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.timezone import datetime,activate
from django.shortcuts import get_object_or_404

import purchases
from .models.models_metadata import (
    Carrier, Vendor
)
from .models.models_data import (
    PURCHASE_REQUEST_STATUSES, Balance, Transaction, PurchaseRequest, Requisitioner
)
from .models.models_apis import (
    Tracker, TrackingWebhookMessage, get_event_data
)
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.db.models import Sum, Count
from django.contrib.auth.mixins import PermissionRequiredMixin
from .forms import PurchaseRequestAccountsFormset, SimpleProductForm, SimpleProductFormset, VendorModelForm

from django_select2.views import AutoResponseView

import datetime as dt
import json
from secrets import compare_digest
from django.utils import timezone

from django.db.transaction import atomic, non_atomic_requests
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, inch
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors, pagesizes
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, PageTemplate, Image
from reportlab.platypus.paragraph import Paragraph
from reportlab.platypus.frames import Frame
from functools import partial

from fdfgen import forge_fdf

from bootstrap_modal_forms.generic import BSModalCreateView

from .forms import AddVendorForm, NewPRForm


# Create your views here.
# class HomeListView(ListView):
#     model = PurchaseRequest

class VendorListView(ListView):
    context_object_name = 'vendors'
    paginate_by = '10'
    queryset = Vendor.objects.order_by('name')

class PurchaseRequestListView(ListView):
    context_object_name = 'purchaserequests'
    paginate_by = '10'
    queryset = PurchaseRequest.objects.order_by('-created_date')

class VendorDetailView(DetailView):
    model = Vendor
    query_pk_and_slug = True

class PurchaseRequestDetailView(DetailView):
    model = PurchaseRequest
    template_name = "purchases/purchaserequest_detail.html"
    context_object_name = 'purchaserequest'
    query_pk_and_slug = True

class VendorCreateView(CreateView):
    form_class = AddVendorForm
    template_name = 'purchases/add_vendor.html'

class VendorModalCreateView(BSModalCreateView):
    template_name = 'purchases/vendor_create_modal.html'
    form_class = VendorModelForm
    success_message = 'Success: New Vendor created.'

class PurchaseRequestCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'purchases.add_purchaserequest'
    # model = PurchaseRequest
    form_class = NewPRForm
    template_name = 'purchases/new_pr.html'
    # success_url = reverse_lazy('purchaserequest_detail')

    def get_context_data(self, **kwargs):
        context = super(PurchaseRequestCreateView, self).get_context_data(**kwargs)
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
        # form.instance.requisitioner = Requisitioner.objects.get(user = self.request.user)
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

        # # Set PR totals and update balance
        self.object.update_totals()
        # ## Update/create balance and create transaction record
        # account = purchase_request_accounts[0].accounts
        # balance, _ = Balance.objects.get_or_create(
        #     account = account,
        #     defaults = {
        #         'balance': 0,
        #         'starting_balance': 0
        #     }
        # )
        # transaction, _ = Transaction.objects.get_or_create(
        #     balance = balance,
        #     purchase_request = self.object,
        #     total_value = -self.object.grand_total
        # )

        # balance.adjust_balance(transaction.total_value)

        # return redirect(reverse_lazy("home"))

        # redirect_url = reverse_lazy('purchaserequest_detail', kwargs={ 'slug': self.object.slug })

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
    # permission_required = 'purchases.change_purchaserequest'
    model = PurchaseRequest
    form_class = NewPRForm
    template_name = "purchases/new_pr.html"
    query_pk_and_slug = True
    # success_url = reverse_lazy('purchaserequest_detail')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['purchase_request_items_formset'] = SimpleProductFormset(self.request.POST, instance=self.object, prefix='items')
            context['purchase_request_accounts_formset'] = PurchaseRequestAccountsFormset(self.request.POST, instance=self.object, prefix='accounts')
        else:
            context['purchase_request_items_formset'] = SimpleProductFormset(instance=self.object, prefix='items')
            context['purchase_request_accounts_formset'] = PurchaseRequestAccountsFormset(instance=self.object, prefix='accounts')
        return context

    def form_valid(self, form): #, purchase_request_items_formset, purchase_request_accounts_formset,purchase_request):
        context = self.get_context_data()
        # form.instance.requisitioner = Requisitioner.objects.get(user = self.request.user)
        self.object = form.save(commit=False)
        
        purchase_request_items_formset = context['purchase_request_items_formset']
        purchase_request_accounts_formset = context['purchase_request_accounts_formset']

        purchase_request_items_formset.save(commit=True)
        purchase_request_accounts_formset.save(commit=True)

        self.object.save()

        self.object.update_totals()

        return redirect(self.object)

    def form_invalid(self, form, purchase_request_items_formset, purchase_request_accounts_formset):
        return self.render_to_response(
            self.get_context_data(
                form=form,
                purchase_request_items_formset=purchase_request_items_formset,
                purchase_request_accounts_formset=purchase_request_accounts_formset
            )
        )

def update_pr_status(request,slug,*args, **kwargs):
    purchase_request = get_object_or_404(PurchaseRequest,slug=slug)
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

    if status_number:
        print("New Status: %s" % new_status)
        purchase_request.status = status_number
        purchase_request.save()

    return redirect(purchase_request)

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
    template_name = "purchases/add_vendor.html"
    query_pk_and_slug = True

class VendorDeleteView(DeleteView):
    model = Vendor
    success_url = reverse_lazy('all_vendors')

    def form_valid(self, *args, **kwargs):
        object = self.get_object()
        object.delete()
        
        redirect_url = redirect_to_next(self, 'all_vendors')

        return redirect(redirect_url)

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
        signature = generate_signature(secret,None)
        # if not compare_digest(given_token,signature):
        #     return HttpResponseForbidden(
        #         "Incorrect token in header.",
        #         content_type="text/plain"
        #     )

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
    estimated_delivery_date = data['track_info']['time_metrics']['estimated_delivery_date']['from']
    last_update_date = data['track_info']['latest_event']['time_utc']
    events = data['track_info']['tracking']['providers'][0]['events']

    try:
        carrier = Carrier.objects.get(carrier_code=carrier_code)
        tracker = Tracker.objects.get(tracking_number=tracking_number,carrier=carrier)
    except:
        raise
    
    if event_type == 'TRACKING_UPDATED':
        tracker.status = status
        tracker.delivery_estimate = estimated_delivery_date
        tracker.events = events
        tracker.save()

    return





    trackings = payload.get('trackings')
    for t in trackings:
        # shipment = t.get('shipment')
        tNumber = shipment.get('trackingNumbers')[0]['tn']
        events = t.get('events')

        shipment_id = shipment.get('shipmentId')
        print("Tracking Number: " + tNumber)
        print("Shipment ID: " + shipment_id)
        # purchase_request = PurchaseRequest .objects.filter(tracker_id=tracker_id).first()
        tracker = Tracker.objects.filter(shipment_id=shipment_id)[0]
        if tracker:
            print("Tracker ID: " + tracker.id)
            tracker.events = events
            tracker.tracking_number = tNumber
            event_data = get_event_data(events[0])
            tracker.status = event_data.get('event_status')
            carrier = Carrier.objects.filter(slug=event_data.get('courier_code'))
            if carrier:
                tracker.carrier = carrier
            else:
                tracker.carrier = None
            tracker.save()

def generate_signature(secret,payload):
    # # given_token = request.headers.get("aftership-hmac-sha256", "")
    # # body = request.body
    # token_byte = bytes(secret, 'UTF-8')
    # hashBytes = hmac.new(token_byte, payload, digestmod=hashlib.sha256)
    # hash = base64.b64encode(hashBytes.digest()).decode()

    hash = "Bearer " + secret

    return hash

def get_tracker(request,instance):
    # tracker_id = instance.tracker_id
    pass

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

# def add_item_modal(request):
#     print("we did something ")
#     return

# class ItemCreateView(BSModalCreateView):
#     template_name = 'purchases/item_create.html'
#     form_class = ItemModalForm
#     suggess_message = 'Success'
#     success_url = reverse_lazy('new_pr')

# class LedgersCreateView(CreateView):
#     model = Transaction
#     form_class = LedgersForm
#     template_name = 'purchases/ledgers_create.html'
#     success_url = reverse_lazy('balances_list')

#     # def post(self, request):
#         # self.success_url = redirect('balances_list')
#         # super().post(self.request.POST)
#         # return redirect('balances_list')

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

# def autocomplete_list(request, model):
#     model_object = apps.get_model(app_label='purchases',model_name='requisitioner')
#     # if not q:
#     object_list = model_object.objects.all()
#     # else:
#     #     object_list = model_object.objects.filter(user__full_name=q)

#     choices = []
#     for object in object_list:
#         choices.append('{ "value": %s, "text": "%s" }' % (object.id,object.user.get_full_name()))

#     response = JsonResponse(choices, safe=False)
#     return response

# class AccountAutoResponseView(AutoResponseView):
    
#     def get(request,*args,**kwargs):
#         self.widget = self.get_widget_or_404()