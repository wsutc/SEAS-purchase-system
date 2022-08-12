import decimal
from xml.dom import NotFoundErr
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
# from .models_apis import Tracker

class Requisitioner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    wsu_id = models.CharField("WSU ID",max_length=50,blank=True,null=True)
    slug = models.SlugField(null=True)
    phone = PhoneNumberField("Phone Number",max_length=25,blank=True,null=True)
    department = models.ForeignKey(Department,on_delete=models.PROTECT)

    class Meta:
        ordering = ['user']

    def save(self, *args, **kwargs):
        self.slug = slugify(self.user.get_full_name(), allow_unicode=True)

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        kwargs = {
            'slug': self.slug,
            'pk': self.pk
        }
        return reverse('requisitioner_detail', kwargs=kwargs)

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

def status_reverse(code:str) -> tuple[str,str]:
    """Return key and value from status list given two-character code."""
    global_vars = globals()
    key = global_vars.get(code.upper(),None)
    if not key:
        return None

    statuses_dict = dict(PURCHASE_REQUEST_STATUSES)
    value = statuses_dict.get(key)

    return (key, value)

class PurchaseRequest(models.Model):
    id = models.AutoField(primary_key=True,editable=False)
    slug = models.SlugField(max_length=255, default='', editable=False)
    requisitioner = models.ForeignKey(Requisitioner,on_delete=models.PROTECT)
    number = models.CharField(max_length=10,blank=True)
    vendor = models.ForeignKey(Vendor,on_delete=models.PROTECT,null=True)
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

    class Meta:
        ordering = ['-created_date']

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
        qs = PurchaseRequest.objects.filter(pk=self.pk)
        subtotal = self.get_subtotal()['extended_price__sum']
        shipping = self.shipping
        tax = round((subtotal + shipping.amount) * decimal.Decimal(self.sales_tax_rate),2)
        total = subtotal + shipping.amount + tax

        qs.update(subtotal=subtotal,sales_tax=tax,grand_total=total)
        return

    def sales_tax_display(self):
        percent = self.sales_tax_rate * 100
        return "%s" % percent

    # def update_tracking(self, events):
    #     last_event = events[0]
    #     self.shipping_status = last_event.get('status')
    #     self.shipping_status_datetime = last_event.get('datetime')
    #     self.save()
        
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

    def __str__(self):
        return self.number

class SimpleProduct(models.Model):
    name = models.CharField(max_length=100)
    purchase_request = models.ForeignKey(PurchaseRequest,on_delete=models.CASCADE)
    manufacturer = models.CharField("Manufacturer (optional)",max_length=50,blank=True,null=True)
    identifier = models.CharField("Part Number/ASIN/etc.",max_length=50,blank=True,null=True)
    link = models.URLField(blank=True,null=True)
    unit_price = models.DecimalField(max_digits=14,decimal_places=2)
    quantity = models.DecimalField(max_digits=14,decimal_places=3,default=1)
    unit = models.ForeignKey(Unit,on_delete=models.PROTECT,default=1)
    extended_price = MoneyField(max_digits=14,decimal_places=2,default_currency='USD',blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields = ('purchase_request','identifier','name'),name='unique_purchase_request_part_number')
        ]

    def extend_price(self):
        extended_price = self.quantity * self.unit_price
        return extended_price

    def save(self, *args, **kwargs):
        self.extended_price = self.extend_price()
        super().save(*args, **kwargs)

    @property
    def vendor(self):
        vendor = self.purchase_request.vendor
        return vendor

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

    def __str__(self):
        return "%s | %s [%s]" % (self.balance.account.account_title,self.purchase_request,self.total_value.amount)