from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
from pyexpat import model

###------------------------------- Item Setup -----------------------------------

class Manufacturer(models.Model):
    name = models.CharField("Name of Manufacturer",max_length=50)
    website = models.URLField("URL of Manufacturer",blank=True)
    wsu_discount = models.BooleanField("Does WSU get a discount?",default=False)
    mfg_logo = models.ImageField("Manufacturer Logo (optional)",blank=True)
    created_date = models.DateTimeField("Date manufacturer added")
    phone = PhoneNumberField("Manufacturer Phone Number (optional)",blank=True)

    def __str__(self):
        return "Manufacturer: %s" % (self.name)

class Vendor(models.Model):
    name = models.CharField("Name of Vendor",max_length=50)
    wsu_discount = models.BooleanField("Does WSU get a discount?",default=False)
    website = models.URLField("URL/Link to Vendor Website")
    vendor_logo = models.ImageField("Vendor Logo (optional)",blank=True)
    phone = PhoneNumberField("Vendor Phone Number",null=False,blank=False)
    street1 = models.CharField("Address 1",max_length=50,blank=False)
    street2 = models.CharField("Address 2 (optional)",max_length=50,blank=True)
    city = models.CharField("City",max_length=50)
    state = models.CharField("State",max_length=50)
    zip = models.CharField("ZIP Code",max_length=10)

    def __str__(self):
        return "Vendor: %s" % (self.name)

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
    description = models.TextField("Description of product")
    created_date = models.DateTimeField("Date Product Created")
    original_manufacturer = models.ForeignKey("Original Manufacturer",Manufacturer)
    specification = models.TextField("Detailed Specifications (required if no specification sheet)")
    spec_sheet = models.FileField("Specifications",upload_to='products',blank=True)
    picture = models.ImageField("Product Image (options)",upload_to='products',blank=True)
    substitution = models.CharField(
        "Product Replacement",
        choices=SUBSTITUTIONS,
        default='buyers_choice'
    )
    approved_substitutes = models.ForeignKey('self',null=True,on_delete=models.PROTECT)
    approved_vendors = models.ForeignKey("Approved Vendor(s)",Vendor,on_delete=models.CASCADE)
    last_price = models.DecimalField("Last Price",decimal_places=2,max_digits=10)

    def __str__(self):
        return "Vendor: %s" % (self.name)

###--------------------------------------- Imported Data -------------------------------------

class Accounts(models.Model):
    account = models.CharField("Account",max_length=10)
    budget_code = models.CharField("Budget Code",max_length=5)
    fund = models.CharField("Fund",max_length=5)
    program_workday = models.CharField("Program Workday",max_length=10)
    account_title = models.CharField("Account Title",max_length=200)

    def __str__(self):
        return "Title: %s" % (self.account_title)

###--------------------------------------- Request Setup -------------------------------------

class Requisitioner(models.Model):
    first_name = models.CharField("First Name",max_length=50,blank=False)
    last_name = models.CharField("Last Name",max_length=50,blank=False)
    phone = models.CharField("Phone Number",max_length=10,blank=False)
    email = models.EmailField("Email",max_length=50,blank=False)

    SEAS = 'seas'
    DEPARTMENTS = (
        (SEAS, 'SEAS'),
    )

    department = models.CharField(
        "Department or Group",
        choices=DEPARTMENTS,
        default='seas'
    )

    def __str__(self):
        return "Name: %s %s" % (self.first_name,self.last_name)

class PurchaseRequest(models.Model):
    id = models.AutoField(primary_key=True,editable=False)
    requisitioner = models.ForeignKey(Requisitioner,on_delete=models.PROTECT)
    number = models.CharField(max_length=10,unique=True)
    products = models.ManyToManyField(Product)
    created_date = models.DateTimeField("Created Date")
    need_by_date = models.DateField("Date Required (optional)",blank=True)
    tax_exempt = models.BooleanField("Tax Exempt?",default=False)
    accounts = models.ManyToManyField(Accounts)
    subtotal = models.DecimalField("Subtotal",decimal_places=2,max_digits=10)
    shipping = models.DecimalField("Shipping ($)",decimal_places=2,max_digits=10)
    sales_tax = models.DecimalField("Sales Tax ($)",decimal_places=2,max_digits=10)
    grand_total = models.DecimalField("Grand Total ($)",decimal_places=2,max_digits=10)
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
        default='PCARD'
    )

    def save(self, *args, **kwargs):
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

class PurchaseOrder(models.Model):
    id = models.AutoField(primary_key=True,editable=False)
    number = models.CharField(max_length=10,unique=True)
    source_PR = models.ManyToManyField("Source Purchase Request(s)",PurchaseRequest)
    vendor = models.ForeignKey("Vendor",Vendor)
    products = models.ManyToManyField(Product)
    created_date = models.DateTimeField("Created Date")
    tax_exempt = models.BooleanField("Tax Exempt?",default=False)
    accounts = models.ManyToManyField(Accounts)
    subtotal = models.DecimalField("Subtotal",decimal_places=2,max_digits=10)
    shipping = models.DecimalField("Shipping ($)",decimal_places=2,max_digits=10)
    sales_tax = models.DecimalField("Sales Tax ($)",decimal_places=2,max_digits=10)
    grand_total = models.DecimalField("Grand Total ($)",decimal_places=2,max_digits=10)

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
