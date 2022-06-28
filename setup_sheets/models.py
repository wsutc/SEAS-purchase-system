from tkinter import CASCADE
from django.db import models
# from psutil import users
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from purchases.models.models_metadata import Manufacturer
from django.utils.text import slugify

# Create your models here.
# class Manufacturer(models.Model):
#     name = models.CharField(max_length=50)
#     website = models.URLField()

#     def __str__(self):
#         return self.name

class ToolComponents(models.Model):
    HOLDER = 'holder'
    INSERT = 'insert'
    COMPONENT_TYPE = (
        (HOLDER, "Tool/Insert Holder"),
        (INSERT, "Insert")
    )

    name = models.CharField("Component Name",max_length=30)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.SET_NULL,null=True)
    product_number = models.CharField("MFG Number",max_length=30)
    tool_type = models.CharField(
        choices=COMPONENT_TYPE,
        default='holder',
        max_length=15
    )

    def __str__(self):
        return self.name

class Tool(models.Model):
    name = models.CharField("Tool Name", max_length=50)
    manufacturer = models.ForeignKey(Manufacturer,on_delete=models.SET_NULL,null=True)
    is_assembly = models.BooleanField("Assembly?")
    tool_holder = models.ForeignKey(ToolComponents,on_delete=models.SET_NULL,null=True,related_name='holder',blank=True)
    tool_insert = models.ForeignKey(ToolComponents,on_delete=models.SET_NULL,null=True,related_name='insert',blank=True)
    product_number = models.CharField("MFG Number (single tool)",max_length=30)
    flutes = models.IntegerField(validators=[MinValueValidator(1)])
    default_position = models.IntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return self.name

class Fixture(models.Model):
    name = models.CharField("Fixture Name", max_length=55)
    part_number = models.CharField(max_length=30)

    def __str__(self):
        return self.name

class Material(models.Model):
    name = models.CharField("Material Name",max_length=30)
    abbreviation = models.CharField("Short Name",max_length=10,blank=True)

    def __str__(self):
        return self.name

class SetupSheet(models.Model):
    name = models.CharField("Setup Name",max_length=50)
    slug = models.SlugField(max_length=255, default='', editable=False)
    part_number = models.CharField(max_length=15)
    part_revision = models.CharField(max_length=10)
    program_name = models.CharField(max_length=30)
    operation = models.CharField(max_length=30)
    material = models.ForeignKey(Material,on_delete=models.SET_NULL,null=True)
    size = models.TextField("Stock Size")
    created_by = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    revision = models.CharField(max_length=2)
    revision_date = models.DateField(auto_now=False, auto_now_add=False)
    tools = models.ManyToManyField(Tool,through='SetupSheetTool')
    notes = models.TextField()
    fixture = models.ForeignKey(Fixture, on_delete=models.SET_NULL, null=True)

    def get_absolute_url(self):
        kwargs = {
            'pk': self.id,
            'slug': self.slug
        }
        return reverse('setup_sheet_detail_view', kwargs=kwargs) 

    def save(self, *args, **kwargs):
        value = self.name
        self.slug = slugify(value, allow_unicode=True)
        super().save(*args, **kwargs)

class SetupSheetTool(models.Model):
    setup_sheet = models.ForeignKey(SetupSheet,on_delete=models.CASCADE)
    tool = models.ForeignKey(Tool,on_delete=models.CASCADE)

    position = models.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        ordering = ('position',)

    def __str__(self):
        return self.setup_sheet.name