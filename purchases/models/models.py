# from re import sub
import http.client, json
import decimal

# from time import strptime
from django.conf import settings
from django.db import models
from django.db.models import Avg, Sum
from django.dispatch import receiver
from django.urls import reverse
from djmoney.models.fields import MoneyField

# from easypost import User
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models.signals import pre_save, post_save

# from django.shortcuts import get_object_or_404
# from django.forms.widgets import Input

# from purchases.forms import PercentField
# from django.dispatch import receiver
# from ..tracking import build_payload
from ..smartsheet import SmartsheetSheet

# from purchases.forms import
# from pyexpat import model

###------------------------------- Item Setup -----------------------------------


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


# class PercentInput(Input):
#     """Form input for percentage"""
#     input_type = 'text'

#     def __format_value(self, value):
#         if value is None:
#             return ''
#         return str(int(value * 100))

#     def render(self, name, value, attrs=None):
#         value = self.__format_value(value)
#         return super().render(name, value, attrs)

#     def _has_changed(self, initial, data):
#         return super()._has_changed(self.__format_value(initial), data)

# class PercentField(models.DecimalField):
#     description = "Human-friendly Percent Display"

#     # widget = PercentInput(attrs={"class":"percentInput", "size":4})

#     default_error_messages = {
#         'positive': 'Must be a positive number.',
#     }

#     # def clean(self, value):
#     #     value = super().clean(value)
#     #     if value is None:
#     #         return None
#     #     if (value < 0):
#     #         raise ValidationError(self.error_messages['positive'])
#     #     return Decimal("%.2f" % (value / 100.0))

# class PercentField(models.DecimalField):
#     description = "Human-readable percent"

#     def __init__(self, *args, **kwargs)


# def save_formset(sender, instance, *args, **kwargs):

# @receiver(post_save, sender=PurchaseRequest)
# def set_subtotal(sender, instance, *args, **kwargs):
#     subtotal = instance.get_subtotal()['extended_price__sum']
#     if subtotal == None:
#         pass
#     elif subtotal != instance.subtotal.amount:
#         instance.subtotal = subtotal
#         instance.save()


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


# class TransactionManager(models.Manager):
#     def get_queryset(self,account:Accounts):
#         queryset = super().get_queryset().filter(account=account)
#         return queryset


# @receiver(post_save, sender=PurchaseRequest)
# def update_balance(sender, instance, created, *args, **kwargs):
#     grand_total = instance.grand_total
#     account = instance.purchase_request.purchaserequestaccounts_set.first().accounts
#     balance, _ = Balance.objects.get_or_create(
#         account=account,
#         defaults= {
#             'balance': 0,
#             'starting_balance': 0
#         }
#     )
#     if created:
#         balance.adjust_balance(grand_total)
