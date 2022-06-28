from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from djmoney.models.fields import MoneyField

from phonenumber_field.modelfields import PhoneNumberField

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
    carrier_code = models.CharField(max_length=30,blank=True,null=True)

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
    cost_center = models.CharField(max_length=15,null=True)

    class Meta:
        verbose_name_plural = "Accounts"

    def __str__(self):
        return "%s (%s)" % (self.program_workday,self.account_title)

class Department(models.Model):
    code = models.CharField("Code/Abbreviation",max_length=10)
    name = models.CharField("Full Department Name",max_length=150)

    def __str__(self):
        return self.name
        
class SpendCategory(models.Model):
    class Meta:
        verbose_name_plural = "Spend Categories"
        
    description = models.TextField("Workday Description",blank=False)
    code = models.CharField("Workday ID",max_length=15,blank=False)
    object = models.CharField(max_length=50)
    subobject = models.CharField(max_length=50)

    def __str__(self):
        return "%s (%s)" % (self.code,self.description)

class DocumentNumber(models.Model):
    document = models.CharField(max_length=50,primary_key=True,unique=True)
    prefix = models.CharField(max_length=10,blank=True,null=True)
    padding_digits = models.IntegerField(blank=True,null=True)
    next_counter = models.IntegerField(default=1)
    last_number = models.CharField(max_length=50,editable=False,null=True)

    def get_next_number(self):
        prefix = self.prefix
        padding_exponent = self.padding_digits - 1
        next_counter = self.next_counter
        number = prefix + str(next_counter + (10 ** padding_exponent))

        self.next_counter = next_counter + 1
        self.last_number = number

        self.save()

        return number