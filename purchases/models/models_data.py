import decimal
from django.conf import settings
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
from djmoney.models.fields import MoneyField
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.db.models import Avg,Sum

from .models_metadata import DocumentNumber, Vendor, Accounts, Carrier, Unit, Urgency, SpendCategory, Department
from .models_apis import Tracker

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

# class SmartsheetRows(models.Model):
#     row_id = models.CharField(max_length=50,primary_key=True,editable=False)
#     number = models.CharField(max_length=30,editable=False)
#     status = models.CharField(max_length=50)
#     requestor = models.ForeignKey(Requisitioner,on_delete=models.PROTECT)
#     required_approver = models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
#     required_approver_approval = models.CharField(max_length=50,null=True)

#     def create(self, *args, **kwargs):
#         sheet = SmartsheetSheet(name=settings.SMARTSHEET_SHEET_NAME)
#         data = [{'Status':'Created'}]
#         response = sheet.add_sheet_rows(data)
#         row = response.data[0]
#         row_id = row.id
#         cells = row.cells
#         number = cells[sheet.columns['Request Number']]
#         self.row_id = row_id

WL = '0'
AA = '1'
AP = '2'
CM = '3'
DN = '4'
RT = '5'
OR = '6'
SH = '7'
RC = '8'
PURCHASE_REQUEST_STATUSES = (
    (WL, 'Wish List/Created'),
    (AA, 'Awaiting Approval'),
    (AP, 'Approved'),
    (OR, 'Ordered'),
    (SH, 'Shipped'),
    (RC, 'Received'),
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

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
        # self.requestor = Requisitioner.get()
        # row = SmartsheetRows.objects.create()

    def get_absolute_url(self):
        kwargs = {
            'slug': self.slug
        }
        return reverse('purchaserequest_detail', kwargs=kwargs)  

    def save(self, *args, **kwargs):
        print(self._state.adding)
        if not self.number:
            doc_number, _ = DocumentNumber.objects.get_or_create(
                document = 'PurchaseRequest',
                defaults = {
                    'prefix': 'PR',
                    'padding_digits': 5,
                }
            )
            self.number = doc_number.get_next_number()
        value = self.number
        self.slug = slugify(value, allow_unicode=True)
        
        super().save(*args, **kwargs)

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
        tax = round((subtotal + shipping.amount) * decimal.Decimal(self.sales_tax_rate),2)
        total = subtotal + shipping.amount + tax

        self.subtotal = subtotal
        self.sales_tax = tax
        self.grand_total = total

        self.save()
        return

    def sales_tax_display(self):
        percent = self.sales_tax_rate * 100
        return "%s" % percent

    def update_tracking(self, events):
        last_event = events[0]
        self.shipping_status = last_event.get('status')
        self.shipping_status_datetime = last_event.get('datetime')
        self.save()
        
    def update_transactions(self):
        if self.purchaserequestaccounts_set.first():
            grand_total = self.grand_total
            account = self.purchaserequestaccounts_set.first().accounts
            balance, _ = Balance.objects.get_or_create(
                account=account,
                defaults= {
                    'balance': 0,
                    'starting_balance': 0
                }
            )
            transaction, created = Transaction.objects.get_or_create(
                purchase_request=self,
                defaults= {
                    'total_value': grand_total,
                    'balance': balance
                }
            )
            if not created:
                transaction.total_value = -grand_total
                transaction.save()

    def get_tracking_link(self):
        if stub := self.carrier.tracking_link:
            return stub + self.tracking_number
        else:
            return None

    # def set_number(self):
    #     if not self.number:
            
    #         request = PurchaseRequest.objects.get(id=self.id)
    #         request.number = number
    #         request.save()

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





    # sheet = SmartsheetSheet(name="Purchase Requests")

    # response = sheet.add_sheet_rows(data)

    # print(response)


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

class PurchaseRequestAccounts(models.Model):
    class Meta:
        verbose_name_plural = "Purchase Request Accounts"
    purchase_request = models.ForeignKey(PurchaseRequest,on_delete=models.CASCADE)
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

    def adjust_balance(self,adjustment_amount:decimal):
        new_balance = self.balance + adjustment_amount
        self.updated_datetime = timezone.now()
        self.balance = new_balance
        self.save()
        return self.balance

    def recalculate_balance(self):
        transactions_sum = Transaction.objects.filter(balance = self).aggregate(Sum('total_value'))
        # SimpleProduct.objects.filter(purchase_request_id=self.id).aggregate(Sum('extended_price'))
        if total_sum := transactions_sum.get('total_value__sum'):
            new_balance = self.starting_balance.amount + total_sum
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
        instance.balance = instance.starting_balance
        instance.save()


class Transaction(models.Model):
    balance = models.ForeignKey(Balance,on_delete=models.CASCADE)
    purchase_request = models.OneToOneField(PurchaseRequest,on_delete=models.CASCADE)
    processed_datetime = models.DateTimeField(auto_now_add=True)
    total_value = MoneyField(max_digits=14,decimal_places=2,default_currency='USD')

    # objects = models.Manager()
    # balance_objects = TransactionManager()

    class Meta:
        # verbose_name_plural = "Ledgers"
        ordering = ['-processed_datetime']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_total = self.total_value

    # def get_absolute_url(self):
    #     kwargs = {
    #         'pk': self.pk
    #     }
    #     return reverse('update_ledger_item', kwargs=kwargs) 

    # def save(self, *args, **kwargs):
    #     balance_account = self.balance
    #     if self.total_value != self.__original_total:
    #         if self.__original_total:
    #             balance_change = self.total_value - self.__original_total
    #         else:
    #             balance_change = self.total_value
    #     else:
    #         balance_change = 0
    #     print("Old Balance: " + str(balance_account.balance.amount))
    #     # if self.pk:
    #     #     existing_value = self.total_value
    #     # else:
    #     new_balance = Balance.add_transaction(balance_account,balance_change)
    #     print("New Balance: " + str(new_balance.amount))
    #     super().save(*args, **kwargs)

    def __str__(self):
        return "%s | %s [%s]" % (self.balance.account.account_title,self.purchase_request,self.total_value.amount)