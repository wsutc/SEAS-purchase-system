from asyncio.windows_events import NULL
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse
from djmoney.models.fields import MoneyField
from phonenumber_field.modelfields import PhoneNumberField
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
    # mfg_logo = models.ImageField("Manufacturer Logo (optional)",blank=True)
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

    name = models.CharField("Name of Product",max_length=50)
    slug = models.SlugField(max_length=255, unique=True, default='', editable=False)
    description = models.TextField("Description of product",max_length=255)
    created_date = models.DateTimeField("Date Product Created",auto_now_add=True)
    original_manufacturer = models.ForeignKey(Manufacturer,on_delete=models.PROTECT)
    specification = models.TextField("Detailed Specifications (required if no specification sheet)")
    spec_sheet = models.FileField("Specifications",upload_to='products',blank=True)
    # picture = models.ImageField("Product Image (options)",upload_to='products',blank=True)
    substitution = models.CharField(
        "Product Replacement",
        choices=SUBSTITUTIONS,
        default='buyers_choice',
        max_length=150
    )
    approved_substitutes = models.ForeignKey('self',null=True,on_delete=models.PROTECT,blank=True)
    approved_vendors = models.ForeignKey(Vendor,on_delete=models.CASCADE,null=True)
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
        return self.name

class Carrier(models.Model):
    name = models.CharField("Name of Carrier",max_length=50)
    tracking_link = models.URLField("URL stub for tracking")
    website = models.URLField("Carrier Website")

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
        return self.account_title

###--------------------------------------- Request Setup -------------------------------------

class Department(models.Model):
    code = models.CharField("Code/Abbreviation",max_length=10)
    name = models.CharField("Full Department Name",max_length=150)

    def __str__(self):
        return self.name

class Requisitioner(models.Model):
    first_name = models.CharField("First Name",max_length=50,blank=False)
    last_name = models.CharField("Last Name",max_length=50,blank=False)
    # slug = models.SlugField(max_length=255, unique=True)
    phone = PhoneNumberField("Phone Number",max_length=10,blank=False)
    email = models.EmailField("Email",max_length=50,blank=False)
    department = models.ForeignKey(Department,on_delete=models.PROTECT)

    def __str__(self):
        return "%s %s" % (self.first_name,self.last_name)

class PurchaseRequest(models.Model):
    id = models.AutoField(primary_key=True,editable=False)
    slug = models.SlugField(max_length=255, default='', editable=False)
    requisitioner = models.ForeignKey(Requisitioner,on_delete=models.PROTECT)
    number = models.CharField(max_length=10,blank=True)
    vendor = models.ForeignKey(Vendor,on_delete=models.PROTECT,null=True)
    # products = models.ManyToManyField(Product,through='PurchaseRequestItems')
    # items = models.ManyToManyField(PurchaseRequestItems)
    created_date = models.DateTimeField("Created Date",auto_now_add=True)
    need_by_date = models.DateField("Date Required (optional)",blank=True,null=True)
    tax_exempt = models.BooleanField("Tax Exempt?",default=False)
    # accounts = models.ManyToManyField(Accounts,through='PurchaseRequestAccounts')
    # subtotal = models.DecimalField("Subtotal",decimal_places=2,max_digits=10)
    shipping = MoneyField("Shipping ($)",decimal_places=2,max_digits=14,default_currency='USD')
    # sales_tax = models.DecimalField("Sales Tax ($)",decimal_places=2,max_digits=10)
    # grand_total = models.DecimalField("Grand Total ($)",decimal_places=2,max_digits=10)
    urgency = models.ForeignKey(Urgency,on_delete=models.PROTECT,default=1)
    justification = models.TextField("Justification",blank=False)
    instruction = models.TextField(
        "Special Instructions",
        default='Because grand total amount does not include shipping/handling and tax costs, Dr. Mo approves if total costs exceeds grand total amount.',
    )

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

    def set_number(self):
        if not self.number:
            number = "PR" + str(self.id + (10 ** 4))            # Creates a number starting with 'PR' and ending with a 5 character (10^4) unique ID
            request = PurchaseRequest.objects.get(id=self.id)
            request.number = number
            request.save()

    def __str__(self):
        return self.number

class PurchaseRequestItems(models.Model):
    product = models.ForeignKey(Product,on_delete=models.PROTECT)
    purchase_request = models.ForeignKey(PurchaseRequest,on_delete=models.PROTECT)

    class Meta:
        verbose_name_plural = "Purchase Request Items"

    quantity = models.DecimalField(blank=False,decimal_places=3,max_digits=14)

    unit = models.ForeignKey(Unit,on_delete=models.PROTECT,default=1)
    price = MoneyField(max_digits=14,decimal_places=2,default_currency='USD',null=True)
    # extended_price = MoneyField(max_digits=14, decimal_places=2, default_currency='USD',default=0)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.extended_price = self.quantity * self.price

    def extend(self):
        extended_price = self.quantity * self.price
        return extended_price

    def __str__(self):
        name = self.product.name
        return name

class PurchaseOrder(models.Model):
    id = models.AutoField(primary_key=True,editable=False)
    # slug = models.SlugField(max_length=255, unique=True)
    number = models.CharField(max_length=10,unique=True)
    # source_PR = models.ManyToManyField("Source Purchase Request(s)",PurchaseRequest)
    vendor = models.ForeignKey("Vendor",Vendor)
    # products = models.ManyToManyField(Product)
    created_date = models.DateTimeField("Created Date",auto_now_add=True)
    tax_exempt = models.BooleanField("Tax Exempt?",default=False)
    # accounts = models.ManyToManyField(Accounts)
    subtotal = models.DecimalField("Subtotal",decimal_places=2,max_digits=10)
    shipping = models.DecimalField("Shipping ($)",decimal_places=2,max_digits=10)
    sales_tax = models.DecimalField("Sales Tax ($)",decimal_places=2,max_digits=10)
    grand_total = models.DecimalField("Grand Total ($)",decimal_places=2,max_digits=10)
    carrier = models.ForeignKey("Carrier",Carrier,blank=True,null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.set_number()

    def set_number(self):
        if not self.number:
            number = "PO" + str(self.id + (10 ** 4))            # Creates a number starting with 'PO' and ending with a 5 character (10^4) unique ID
            request = PurchaseOrder.objects.get(id=self.id)
            request.number = number
            request.save()

    def __str__(self):
        return self.number

class PurchaseOrderItems(models.Model):
    product = models.ForeignKey(Product,on_delete=models.PROTECT)
    purchase_order = models.ForeignKey(PurchaseOrder,on_delete=models.PROTECT)

    quantity = models.DecimalField(blank=False,decimal_places=3,max_digits=3)

    unit = models.ForeignKey(Unit, on_delete=models.PROTECT,default=1)

    def __str__(self):
        return self.id

class SpendCategory(models.Model):
    class Meta:
        verbose_name_plural = "Spend Categories"
        
    description = models.TextField("Workday Description",blank=False)
    code = models.CharField("Workday ID",max_length=15,blank=False)
    object = models.CharField(max_length=50)
    subobject = models.CharField(max_length=50)

    def __str__(self):
        return self.description

class PurchaseRequestAccounts(models.Model):
    class Meta:
        verbose_name_plural = "Purchase Request Accounts"
    purchase_request = models.ForeignKey(PurchaseRequest,on_delete=models.PROTECT)
    accounts = models.ForeignKey(Accounts,on_delete=models.PROTECT)

    spend_category = models.ForeignKey(SpendCategory,on_delete=models.PROTECT)
    distribution_amount = MoneyField("Distribution",max_digits=14,decimal_places=2,default_currency='USD',blank=True,null=True)
    distribution_percent = models.FloatField(default=0)