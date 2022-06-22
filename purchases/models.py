from ast import If
from asyncio.windows_events import NULL
import decimal
from re import sub
import http.client, json
from time import strptime
from django.conf import settings
from django.db import models
from django.db.models import Avg,Sum
from django.dispatch import receiver
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse
from djmoney.models.fields import MoneyField
# from easypost import User
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models.signals import pre_save, post_save
# from django.dispatch import receiver
from .tracking import TrackerOld, build_payload

# from purchases.forms import  
# from pyexpat import model

###------------------------------- Item Setup -----------------------------------

class State(models.Model):
    name = models.CharField(max_length=50)
    abbreviation = models.CharField(max_length=2)

    def __str__(self):
        return self.name

class Manufacturer(models.Model):
    name = models.CharField("Name of Manufacturer",max_length=50)
    slug = models.SlugField(max_length=255, unique=True, default='', editable=False)
    website = models.URLField("URL of Manufacturer",blank=True)
    wsu_discount = models.BooleanField("Does WSU get a discount?",default=False)
    discount_percentage = models.FloatField(default=0)
    mfg_logo = models.ImageField("Manufacturer Logo (optional)",upload_to='manufacturers',blank=True)
    created_date = models.DateTimeField("Date manufacturer added",auto_now_add=True)
    phone = PhoneNumberField("Manufacturer Phone Number (optional)",blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        kwargs = {
            'pk': self.id,
            'slug': self.slug
        }
        return reverse('manufacturer_detail', kwargs=kwargs)  

    def save(self, *args, **kwargs):
        value = self.name
        self.slug = slugify(value, allow_unicode=True)
        super().save(*args, **kwargs)

class Vendor(models.Model):
    name = models.CharField("Name of Vendor",max_length=50)
    slug = models.SlugField(max_length=255, unique=True, default='', editable=False)
    wsu_discount = models.BooleanField("Does WSU get a discount?",default=False)
    discount_percentage = models.FloatField(default=0)
    website = models.URLField("URL/Link to Vendor Website")
    # vendor_logo = models.ImageField("Vendor Logo (optional)",blank=True)
    phone = PhoneNumberField("Vendor Phone Number",null=False,blank=True)
    street1 = models.CharField("Address 1",max_length=50,blank=True)
    street2 = models.CharField("Address 2 (optional)",max_length=50,blank=True)
    city = models.CharField("City",max_length=50,blank=True)
    # state = models.CharField("State",max_length=50,blank=True)
    state = models.ForeignKey("State",State,blank=True,null=True)
    zip = models.CharField("ZIP Code",max_length=10,blank=True)
    email = models.EmailField(max_length=60,blank=True,null=True)

    def get_absolute_url(self):
        kwargs = {
            'pk': self.id,
            'slug': self.slug
        }
        return reverse('vendor_detail', kwargs=kwargs)  

    def save(self, *args, **kwargs):
        value = self.name
        self.slug = slugify(value, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Product(models.Model):
    FREE = 'buyers_choice'
    STRICT = 'strict'
    ASK = 'ask_before'
    SUBSTITUTIONS = (
        (FREE, 'Substitute with like product'),
        (STRICT, 'No substitutions allowed'),
        (ASK, 'Ask before substituting'),
    )

    name = models.CharField("Name of Product",max_length=40)
    slug = models.SlugField(max_length=255, unique=True, default='', editable=False)
    description = models.TextField("Description of product",max_length=255)
    created_date = models.DateTimeField("Date Product Created",auto_now_add=True)
    original_manufacturer = models.ForeignKey(Manufacturer,on_delete=models.PROTECT)
    specification = models.TextField("Detailed Specifications (required if no specification sheet)",blank=True,null=True)
    spec_sheet = models.FileField("Specification Sheet",upload_to='products',blank=True,null=True)
    picture = models.ImageField("Product Image (optional)",upload_to='products',blank=True)
    substitution = models.CharField(
        "Product Replacement",
        choices=SUBSTITUTIONS,
        default='buyers_choice',
        max_length=150,
        blank="True"
    )
    approved_substitutes = models.ForeignKey('self',null=True,on_delete=models.PROTECT,blank=True)
    approved_vendors = models.ForeignKey(Vendor,on_delete=models.CASCADE,null=True)
    vendor_number = models.CharField("Vendor ID Number",max_length=30,blank=True,null=True)
    last_price = MoneyField("Last Price",max_digits=14, decimal_places=2, default_currency='USD')
    # last_price = models.DecimalField("Last Price",decimal_places=2,max_digits=10)
    link = models.URLField("Direct Link",blank=True)
    identifier = models.CharField("Unique Identifier (ASIN/UPC/PN/etc.)",max_length=50,blank=True)
    tax_exempt = models.BooleanField("Tax Exempt?",default=False)

    def get_absolute_url(self):
        kwargs = {
            'pk': self.id,
            'slug': self.slug
        }
        return reverse('product_detail', kwargs=kwargs)  

    def save(self, *args, **kwargs):
        value = self.name
        self.slug = slugify(value, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return "%s [%s] (%s)" % (self.name,self.original_manufacturer,self.identifier)

class Carrier(models.Model):
    name = models.CharField("Name of Carrier",max_length=50)
    tracking_link = models.URLField("URL stub for tracking",blank=True)
    website = models.URLField("Carrier Website",blank=True)
    slug = models.CharField("Carrier Slug",max_length=10,blank=True,null=True)

    def __str__(self):
        return self.name

class Unit(models.Model):
    unit = models.CharField(max_length=25)
    abbreviation = models.CharField(max_length=4)

    def __str__(self):
        name = self.abbreviation
        return name

class Urgency(models.Model):
    name = models.CharField(unique=True,max_length=50)
    note = models.TextField(blank=False)

    class Meta:
        verbose_name_plural = "Urgencies"

    def __str__(self):
        name = self.name
        return name

###--------------------------------------- Imported Data -------------------------------------

class Accounts(models.Model):
    account = models.CharField("Account",max_length=10)
    budget_code = models.CharField("Budget Code",max_length=5)
    fund = models.CharField("Fund",max_length=5)
    grant = models.CharField(max_length=15,blank=True)
    gift = models.CharField(max_length=15,blank=True)
    program_workday = models.CharField("Program Workday",max_length=10)
    account_title = models.CharField("Account Title",max_length=200)

    class Meta:
        verbose_name_plural = "Accounts"

    def __str__(self):
        return "%s (%s)" % (self.program_workday,self.account_title)

###--------------------------------------- Helper Tables -------------------------------------

# class Status(models.Model):
#     name = models.CharField(max_length=30)
#     PR = 'purchase_request'
#     PO = 'purchase_order'
#     VALID_FOR = (
#         (PO, 'PURCHASE ORDER'),
#         (PR, 'PURCHASE REQUEST')
#     )
#     purchase_type = models.CharField(
#         "Choose One",
#         choices=VALID_FOR,
#         default='pcard',
#         max_length=150
#     )


###--------------------------------------- Request Setup -------------------------------------

class Department(models.Model):
    code = models.CharField("Code/Abbreviation",max_length=10)
    name = models.CharField("Full Department Name",max_length=150)

    def __str__(self):
        return self.name

class Requisitioner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    wsu_id = models.CharField("WSU ID",max_length=50,blank=True,null=True)
    # first_name = models.CharField("First Name",max_length=50,blank=False)
    # last_name = models.CharField("Last Name",max_length=50,blank=False)
    # slug = models.SlugField(max_length=255, unique=True)
    phone = PhoneNumberField("Phone Number",max_length=25,blank=True,null=True)
    # email = models.EmailField("Email",max_length=50,blank=False)
    department = models.ForeignKey(Department,on_delete=models.PROTECT)

    def __str__(self):
        return self.user.get_full_name()

class Tracker(models.Model):
    id = models.CharField(max_length=100, primary_key=True, editable=False)
    carrier = models.ForeignKey(Carrier,on_delete=models.PROTECT,blank=True,null=True)
    tracking_number = models.CharField(max_length=100)
    events = models.JSONField(default=None,blank=True,null=True)
    shipment_id = models.CharField(max_length=100,blank=True,null=True)
    status = models.CharField(max_length=50,blank=True,null=True)
    delivery_estimate = models.DateTimeField(blank=True,null=True)

    class Meta:
        indexes = [
            models.Index(fields=['id'])
        ]

    def update(self):
        api_key = settings.SHIP24_KEY
        # id = self.id
        tracking_number = self.tracking_number
        conn = http.client.HTTPSConnection("api.ship24.com")
        headers = {
            'Content-Type': "application/json",
            'Authorization': "Bearer " + api_key
        }

        get_path = "/public/v1/trackers/search/%s" % (tracking_number)

        conn.request("GET", get_path, headers=headers)
        response = conn.getresponse()
        data = response.read()
        dataJson = json.loads(data.decode("utf-8"))
        # print(dataJson)
        dataDict = dataJson.get('data')
        trackings = dataDict.get('trackings')
        # tracker = trackings[0].get('tracker')
        shipment = trackings[0].get('shipment')
        events = trackings[0].get('events')
        event_data = get_event_data(events[0])

        carrier = Carrier.objects.get(slug = event_data.get('courier_code'))
        if carrier:
            self.carrier = carrier
        self.shipment_id = shipment.get('shipmentId')
        
        self.delivery_estimate = shipment.get('delivery').get('estimatedDeliveryDate')
        self.events = events
        if status := shipment.get('statusCode'):
            self.status = status
        elif status := event_data.get('event_status'):
            self.status = status
        self.save()

    def __str__(self):
        return str(self.id)

def get_event_data(event):
    event_data = {
        'event_id': event.get('eventId'),
        'event_status': event.get('status'),
        'event_datetime': event.get('datetime'),
        'courier_code': event.get('courierCode')
    }

    return event_data

@receiver(pre_save, sender=Tracker)
def get_tracker(sender, instance, *args, **kwargs):
    api_key = settings.SHIP24_KEY

    conn = http.client.HTTPSConnection("api.ship24.com")
    headers = {
        'Content-Type': "application/json",
        'Authorization': "Bearer " + api_key
    }

    if instance.carrier:
        carrier_slug = instance.carrier.slug
    else:
        carrier_slug = None
    tracking_number = instance.tracking_number

    payload = build_payload(tracking_number, carrier_slug)

    conn.request("POST", "/public/v1/trackers", payload, headers)

    response = conn.getresponse()
    data = response.read()
    dataJson = json.loads(data.decode("utf-8"))

    tracking = dataJson['data']['tracker']

    if str(response.status).startswith('2'):
        instance.id = tracking['trackerId']
        instance.tracking_number = tracking['trackingNumber']
        # instance.events = dataJson.get('events')

WL = '0'
AA = '1'
AP = '2'
CM = '3'
DN = '4'
RT = '5'
PURCHASE_REQUEST_STATUSES = (
    (WL, 'Wish List/Created'),
    (AA, 'Awaiting Approval'),
    (AP, 'Approved, Awaiting PO Creation'),
    (CM, 'Complete'),
    (DN, 'Denied (no resubmission)'),
    (RT, 'Returned (please resubmit)')
)

class PurchaseRequest(models.Model):
    id = models.AutoField(primary_key=True,editable=False)
    slug = models.SlugField(max_length=255, default='', editable=False)
    requisitioner = models.ForeignKey(Requisitioner,on_delete=models.PROTECT)
    number = models.CharField(max_length=10,blank=True)
    vendor = models.ForeignKey(Vendor,on_delete=models.PROTECT,null=True)
    # items = models.ManyToManyField(Product,through='PurchaseRequestItems')
    created_date = models.DateTimeField("Created Date",auto_now_add=True)
    need_by_date = models.DateField("Date Required (optional)",blank=True,null=True)
    tax_exempt = models.BooleanField("Tax Exempt?",default=False)
    accounts = models.ManyToManyField(Accounts,through='PurchaseRequestAccounts')
    subtotal = MoneyField("Subtotal",decimal_places=2,max_digits=14,default_currency='USD',default=0)
    shipping = MoneyField("Shipping ($)",decimal_places=2,max_digits=14,default_currency='USD',default=0)
    sales_tax_rate = models.DecimalField(max_digits=5,decimal_places=3,default=settings.DEFAULT_TAX_RATE)
    sales_tax = MoneyField("Sales Tax ($)",decimal_places=2,max_digits=14,default_currency='USD',default=0)
    grand_total = MoneyField("Grand Total ($)",decimal_places=2,max_digits=14,default_currency='USD',default=0)
    urgency = models.ForeignKey(Urgency,on_delete=models.PROTECT,default=1)
    justification = models.TextField("Justification",blank=False)
    instruction = models.TextField(
        "Special Instructions",
        default=settings.DEFAULT_INSTRUCTIONS,
    )
    carrier = models.ForeignKey("Carrier",Carrier,blank=True,null=True)
    tracking_number = models.CharField(max_length=55,blank=True,null=True)
    tracker = models.ForeignKey(Tracker,on_delete=models.SET_NULL,blank=True,null=True)

    PO = 'po'
    PCARD = 'pcard'
    IRI = 'iri'
    INV_VOUCHER = 'invoice voucher'
    CONTRACT = 'contract'
    PURCHASE_TYPE = (
        (PO, 'PURCHASE ORDER'),
        (PCARD, 'PCARD'),
        (IRI, 'IRI'),
        (INV_VOUCHER, 'INVOICE VOUCHER'),
        (CONTRACT, 'CONTRACT')
    )
    purchase_type = models.CharField(
        "Choose One",
        choices=PURCHASE_TYPE,
        default='pcard',
        max_length=150
    )

    status = models.CharField(
        choices=PURCHASE_REQUEST_STATUSES,
        default='0',
        max_length=150
    )

    def get_absolute_url(self):
        kwargs = {
            'slug': self.slug
        }
        return reverse('purchaserequest_detail', kwargs=kwargs)  

    def save(self, *args, **kwargs):
        value = self.number
        self.slug = slugify(value, allow_unicode=True)
        
        super().save(*args, **kwargs)
        self.set_number()

    def get_subtotal(self):
        extended_price = SimpleProduct.objects.filter(purchase_request_id=self.id).aggregate(Sum('extended_price'))
        if extended_price['extended_price__sum'] != None:
            pass
        else:
            extended_price['extended_price__sum'] = 0
        return extended_price

    def update_totals(self):
        subtotal = self.get_subtotal()['extended_price__sum']
        shipping = self.shipping
        tax = round((subtotal + shipping.amount) * decimal.Decimal(settings.DEFAULT_TAX_RATE),2)
        total = subtotal + shipping.amount + tax

        self.subtotal = subtotal
        self.sales_tax = tax
        self.grand_total = total

        self.save()
        return

    def update_tracking(self, events):
        last_event = events[0]
        self.shipping_status = last_event.get('status')
        self.shipping_status_datetime = last_event.get('datetime')
        self.save()

    def get_tracking_link(self):
        if stub := self.carrier.tracking_link:
            return stub + self.tracking_number
        else:
            return None

    def set_number(self):
        if not self.number:
            number = "PR" + str(self.id + (10 ** 4))            # Creates a number starting with 'PR' and ending with a 5 character (10^4) unique ID
            request = PurchaseRequest.objects.get(id=self.id)
            request.number = number
            request.save()

    def __str__(self):
        return self.number

################## This is the "good" one ######################
# @receiver(pre_save, sender=PurchaseRequest)
# def get_tracking(sender, instance, *args, **kwargs):
#     if not instance.tracker_id and instance.tracking_number:
#         # carrier = instance.carrier
#         tracking_number = instance.tracking_number
#         # tracker_created = instance.tracker_created
#         api_key = settings.SHIP24_KEY

#         tracker = TrackerOld.get('slug',tracking_number,api_key)
#         # instance.tracker_created = True

#         # instance.tracking_link = tracker.courier_tracking_link
#         # instance.shipping_status = tracker.tag
#         # instance.tracker_active = tracker.active
#         instance.tracker_id = tracker.id

# def update_tracking(instance)

@receiver(pre_save, sender=PurchaseRequest)
def create_tracker(sender, instance, *args, **kwargs):
    if not instance.tracker and instance.tracking_number:
        carrier = instance.carrier
        tracking_number = instance.tracking_number

        tracker = Tracker.objects.get_or_create(carrier=carrier,tracking_number=tracking_number)
        # tracker = Tracker.objects.get(id=tracker.id)
        instance.tracker = tracker[0]
        # Tracker.update(tracker[0])

@receiver(post_save, sender=PurchaseRequest)
def update_tracker(sender, instance, *args, **kwargs):
    if tracker := instance.tracker:
        Tracker.update(tracker)

# def save_formset(sender, instance, *args, **kwargs):

# @receiver(post_save, sender=PurchaseRequest)
# def set_subtotal(sender, instance, *args, **kwargs):
#     subtotal = instance.get_subtotal()['extended_price__sum']
#     if subtotal == None:
#         pass
#     elif subtotal != instance.subtotal.amount:
#         instance.subtotal = subtotal
#         instance.save()

class SimpleProduct(models.Model):
    name = models.CharField(max_length=100)
    purchase_request = models.ForeignKey(PurchaseRequest,on_delete=models.CASCADE)
    identifier = models.CharField("Part Number/ASIN/etc.",max_length=50,blank=True,null=True)
    link = models.URLField(blank=True,null=True)
    unit_price = models.DecimalField(max_digits=14,decimal_places=2)
    quantity = models.DecimalField(max_digits=14,decimal_places=3,default=1)
    unit = models.ForeignKey(Unit,on_delete=models.PROTECT,default=1)
    extended_price = MoneyField(max_digits=14,decimal_places=2,default_currency='USD',blank=True)

    def extend_price(self):
        extended_price = self.quantity * self.unit_price
        return extended_price

    def save(self, *args, **kwargs):
        self.extended_price = self.extend_price()
        super().save(*args, **kwargs)

    def __str__(self):
        name = self.name
        return name


# class PurchaseRequestItems(models.Model):
#     product = models.ForeignKey(Product,on_delete=models.PROTECT)
#     purchase_request = models.ForeignKey(PurchaseRequest,on_delete=models.CASCADE)

#     class Meta:
#         verbose_name_plural = "Purchase Request Items"

#     quantity = models.DecimalField(blank=False,decimal_places=3,max_digits=14)

#     unit = models.ForeignKey(Unit,on_delete=models.PROTECT,default=1)
#     price = MoneyField(max_digits=14,decimal_places=2,default_currency='USD',null=True,blank=True)
#     extended_price = MoneyField(max_digits=14, decimal_places=2, default_currency='USD',default=0)

#     def extend(self):
#         extended_price = self.quantity * self.price
#         return extended_price

#     def save(self, *args, **kwargs):
#         if not self.price:
#             self.price = self.product.last_price
#         self.extended_price = self.extend()
#         super().save(*args, **kwargs)

#     def __str__(self):
#         name = self.product.name
#         return name

# class PurchaseOrder(models.Model):
#     id = models.AutoField(primary_key=True,editable=False)
#     slug = models.SlugField(max_length=255, default='', editable=False)
#     number = models.CharField(max_length=10,unique=True,blank=True)
#     requisitioner = models.ForeignKey(Requisitioner,on_delete=models.PROTECT)
#     source_purchase_request = models.ForeignKey(PurchaseRequest,on_delete=models.PROTECT)
#     vendor = models.ForeignKey("Vendor",Vendor)
#     items = models.ManyToManyField(Product,through='PurchaseOrderItems')
#     # products = models.ManyToManyField(Product)
#     created_date = models.DateTimeField("Created Date",auto_now_add=True)
#     tax_exempt = models.BooleanField("Tax Exempt?",default=False)
#     accounts = models.ManyToManyField(Accounts,through='PurchaseOrderAccounts')
#     # accounts = models.ManyToManyField(Accounts)
#     # subtotal = models.DecimalField("Subtotal",decimal_places=2,max_digits=10)
#     shipping = MoneyField("Shipping ($)",decimal_places=2,max_digits=14,default_currency='USD',default=0)
#     sales_tax = models.DecimalField("Sales Tax ($)",decimal_places=2,max_digits=10)
#     grand_total = models.DecimalField("Grand Total ($)",decimal_places=2,max_digits=10)
#     carrier = models.ForeignKey("Carrier",Carrier,blank=True,null=True)
#     tracking_number = models.CharField(max_length=55,blank=True,null=True)
#     tracking_link = models.URLField(blank=True, null=True)
#     tracker_created = models.BooleanField(default=False)
#     shipping_status = models.CharField(max_length=55,blank=True,null=True)
#     tracker_active = models.BooleanField(default=True)
#     tracker_id = models.CharField(max_length=100,blank=True,null=True)

#     PO = 'po'
#     PCARD = 'pcard'
#     IRI = 'iri'
#     INV_VOUCHER = 'invoice voucher'
#     CONTRACT = 'contract'
#     PURCHASE_TYPE = (
#         (PO, 'PURCHASE ORDER'),
#         (PCARD, 'PCARD'),
#         (IRI, 'IRI'),
#         (INV_VOUCHER, 'INVOICE VOUCHER'),
#         (CONTRACT, 'CONTRACT')
#     )
#     purchase_type = models.CharField(
#         "Choose One",
#         choices=PURCHASE_TYPE,
#         default='pcard',
#         max_length=150
#     )

#     CR = '0'
#     OR = '1'
#     SH = '2'
#     RC = '3'
#     CH = '4'
#     STATUSES = (
#         (CR, 'Created'),
#         (OR, 'Ordered'),
#         (SH, 'Shipped'),
#         (RC, 'Recieved'),
#         (CH, 'Changed Required')
#     )
#     status = models.CharField(
#         choices=STATUSES,
#         default='created',
#         max_length=150
#     )

#     def get_absolute_url(self):
#         kwargs = {
#             'slug': self.slug
#         }
#         return reverse('purchaseorder_detail', kwargs=kwargs)  

#     def get_tracking_link(self):
#         return self.carrier.tracking_link + self.tracking_number

#     def save(self, *args, **kwargs):
#         value = self.number
#         self.slug = slugify(value, allow_unicode=True)
#         super().save(*args, **kwargs)
#         self.set_number()

#     # def get_tracking(self, *args, **kwargs):
#     #     carrier = self.carrier
#     #     tracking_number = self.tracking_number

#     def update_tracking(self, events):
#         self.shipping_status = events[0].get('status')
#         self.save()

#     def set_number(self):
#         if not self.number:
#             number = "PO" + str(self.id + (10 ** 4))            # Creates a number starting with 'PO' and ending with a 5 character (10^4) unique ID
#             request = PurchaseOrder.objects.get(id=self.id)
#             request.number = number
#             request.save()

#     def __str__(self):
#         return self.number


# # TODO - invert commented lines!
# @receiver(pre_save, sender=PurchaseOrder)
# def get_tracking(sender, instance, *args, **kwargs):
#     if instance.tracking_number:       # and not instance.tracker_id:
#         # carrier = instance.carrier
#         tracking_number = instance.tracking_number
#         tracker_created = instance.tracker_created
#         api_key = settings.SHIP24_KEY

#         tracker = TrackerOld.get('slug',tracking_number,tracker_created,api_key)
#         instance.tracker_created = True

#         # instance.tracking_link = tracker.courier_tracking_link
#         # instance.shipping_status = tracker.tag
#         # instance.tracker_active = tracker.active
#         if not instance.tracker_id:
#             instance.tracker_id = tracker.id
#     # pass

# class PurchaseOrderItems(models.Model):
#     product = models.ForeignKey(Product,on_delete=models.PROTECT)
#     purchase_order = models.ForeignKey(PurchaseOrder,on_delete=models.PROTECT)

#     class Meta:
#         verbose_name_plural = "Purchase Order Items"

#     quantity = models.DecimalField(blank=False,decimal_places=3,max_digits=14)

#     unit = models.ForeignKey(Unit,on_delete=models.PROTECT,default=1)
#     price = MoneyField(max_digits=14,decimal_places=2,default_currency='USD',null=True)
#     # extended_price = MoneyField(max_digits=14, decimal_places=2, default_currency='USD',default=0)

#     def save(self, *args, **kwargs):
#         super().save(*args, **kwargs)
#         self.extended_price = self.quantity * self.price

#     def extend(self):
#         extended_price = self.quantity * self.price
#         return extended_price

#     def __str__(self):
#         name = self.product.name
#         return name

class SpendCategory(models.Model):
    class Meta:
        verbose_name_plural = "Spend Categories"
        
    description = models.TextField("Workday Description",blank=False)
    code = models.CharField("Workday ID",max_length=15,blank=False)
    object = models.CharField(max_length=50)
    subobject = models.CharField(max_length=50)

    def __str__(self):
        return "%s (%s)" % (self.code,self.description)

class PurchaseRequestAccounts(models.Model):
    class Meta:
        verbose_name_plural = "Purchase Request Accounts"
    purchase_request = models.ForeignKey(PurchaseRequest,on_delete=models.PROTECT)
    accounts = models.ForeignKey(Accounts,on_delete=models.PROTECT)

    spend_category = models.ForeignKey(SpendCategory,on_delete=models.PROTECT)
    # distribution_amount = MoneyField("Distribution",max_digits=14,decimal_places=2,default_currency='USD',blank=True,null=True)
    # distribution_percent = models.FloatField(default=0)

    PERCENT = 'percent'
    AMOUNT = 'amount'
    DISTRIBUTION_TYPE = (
        (PERCENT, 'Percent'),
        (AMOUNT, 'Amount')
    )
    distribution_type = models.CharField(
        choices=DISTRIBUTION_TYPE,
        default='percent',
        max_length=15
    )

    distribution_input = models.FloatField(default=100)

    def __str__(self):
        return "%s | %s" % (self.accounts.program_workday,self.spend_category.code)

# class PurchaseOrderAccounts(models.Model):
#     class Meta:
#         verbose_name_plural = "Purchase Order Accounts"
#     purchase_order = models.ForeignKey(PurchaseOrder,on_delete=models.PROTECT)
#     accounts = models.ForeignKey(Accounts,on_delete=models.PROTECT)

#     spend_category = models.ForeignKey(SpendCategory,on_delete=models.PROTECT)
#     distribution_amount = MoneyField("Distribution",max_digits=14,decimal_places=2,default_currency='USD',blank=True,null=True)
#     distribution_percent = models.FloatField(default=0)

#     def __str__(self):
#         return self.spend_category

class TrackingWebhookMessage(models.Model):
    received_at = models.DateTimeField(help_text="DateTime that message was recieved.")
    payload = models.JSONField(default=None, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['received_at'])
        ]

###--------------------------------------- Accounting ----------------------------------------

class Balance(models.Model):
    account = models.OneToOneField(Accounts,on_delete=models.CASCADE)
    balance = MoneyField(max_digits=14,decimal_places=2,default_currency='USD')
    updated_datetime = models.DateTimeField(auto_now_add=True)
    starting_balance = MoneyField(max_digits=14,decimal_places=2,default_currency='USD',default=0)

    # class Meta:
        # verbose_name_plural = "Balances"
        
    def get_absolute_url(self):
        kwargs = {
            'pk': self.pk
        }
        return reverse('balances_detail', kwargs=kwargs)

    def update_balance(self,ledger_value:decimal):
        new_balance = self.balance + ledger_value
        self.balance = new_balance
        self.updated_datetime = timezone.now()
        self.save()
        return self.balance

    def update_balance_complete(self):
        ledger_total_value = Transaction.objects.filter(account = self).aggregate(Sum('total_value'))
        # SimpleProduct.objects.filter(purchase_request_id=self.id).aggregate(Sum('extended_price'))
        if ledger_total_value.get('total_value__sum'):
            new_balance = self.starting_balance.amount + ledger_total_value.get('total_value__sum')
        else:
            new_balance = self.starting_balance
        self.updated_datetime = timezone.now()
        self.balance = new_balance
        self.save()

    def __str__(self):
        return "%s [%s]" % (self.account.account_title,self.balance.amount)

@receiver(post_save, sender=Balance)
def set_initial_balance(sender, instance, created, **kwargs):
    if created:
        instance.balance = instance.initial_balance
        instance.save()

class TransactionManager(models.Manager):
    def get_queryset(self,account:Accounts):
        queryset = super().get_queryset().filter(account=account)
        return queryset

class Transaction(models.Model):
    balance = models.ForeignKey(Balance,on_delete=models.CASCADE)
    purchase_request = models.OneToOneField(PurchaseRequest,on_delete=models.CASCADE)
    processed_datetime = models.DateTimeField(auto_now_add=True)
    total_value = MoneyField(max_digits=14,decimal_places=2,default_currency='USD')

    objects = models.Manager()
    balance_objects = TransactionManager()

    class Meta:
        # verbose_name_plural = "Ledgers"
        ordering = ['-processed_datetime']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_total = self.total_value

    def get_absolute_url(self):
        kwargs = {
            'pk': self.pk
        }
        return reverse('update_ledger_item', kwargs=kwargs) 

    def save(self, *args, **kwargs):
        balance_account = self.balance
        if self.total_value != self.__original_total:
            if self.__original_total:
                balance_change = self.total_value - self.__original_total
            else:
                balance_change = self.total_value
        else:
            balance_change = 0
        print("Old Balance: " + str(balance_account.balance.amount))
        # if self.pk:
        #     existing_value = self.total_value
        # else:
        new_balance = Balance.update_balance(balance_account,balance_change)
        print("New Balance: " + str(new_balance.amount))
        super().save(*args, **kwargs)

    def __str__(self):
        return "%s | %s [%s]" % (self.balance.account.account_title,self.purchase_request,self.total_value.amount)