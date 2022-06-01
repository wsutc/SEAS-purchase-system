from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from django.core.validators import MinValueValidator #, MaxValueValidator

from purchases.models import Manufacturer, Product, PurchaseOrder

# Create your models here.
class Department(models.Model):
    name = models.CharField(max_length=100)
    tag_prefix = models.CharField(max_length=10)

    def __str__(self):
        return self.name

class Building(models.Model):
    name = models.CharField(max_length=100)
    prefix = models.CharField(max_length=5)

    def __str__(self):
        return self.name

class Room(models.Model):
    id = models.AutoField(primary_key=True,editable=False)
    slug = models.SlugField(max_length=255, default='', editable=False)
    name = models.CharField(max_length=100)
    building = models.ForeignKey(Building,on_delete=models.PROTECT)
    number = models.IntegerField(validators=[MinValueValidator(100)])
    full_number = models.CharField(max_length=15,blank=True)

    def set_full_number(self):
        if not self.full_number:
            full_number = self.building.prefix + str(self.number)
            room = Room.objects.get(id=self.id)
            room.full_number = full_number
            room.save()

    def get_absolute_url(self):
        kwargs = {
            'id': self.id,
            'slug': self.slug
        }
        return reverse('purchaserequest_detail', kwargs=kwargs)

    def save(self, *args, **kwargs):
        value = self.full_number
        self.slug = slugify(value, allow_unicode=True)
        super().save(*args, **kwargs)
        self.set_full_number()

    def __str__(self):
        return self.name

class Item(models.Model):
    id = models.AutoField(primary_key=True,editable=False)
    slug = models.SlugField(max_length=255, default='', editable=False)
    name = models.CharField(max_length=50,blank=False)
    room = models.ForeignKey(Room,on_delete=models.SET_NULL,blank=False,null=True)
    description = models.TextField(blank=False)
    manufacturer = models.ForeignKey(Manufacturer,on_delete=models.SET_NULL,blank=True,null=True)
    product = models.ForeignKey(Product,on_delete=models.SET_NULL,blank=True,null=True)
    accessory = models.ManyToManyField("self",through="EquipmentAccessory",through_fields=("item","accessory"))
    equipment_tag = models.CharField(max_length=30,blank=True,null=True)
    department = models.ForeignKey(Department,on_delete=models.PROTECT,blank=True)
    serial_number = models.CharField(max_length=50,blank=True,null=True)
    manufacture_date = models.DateField(blank=True,null=True)
    purchase_date = models.DateField(blank=True,null=True)
    product = models.ForeignKey(Product,on_delete=models.SET_NULL,blank=True,null=True)
    purchase_order = models.ForeignKey(PurchaseOrder,on_delete=models.SET_NULL,blank=True,null=True)

    ACCESSORY = 'accessory'
    CONSUMABLE = 'consumable'
    EQUIPMENT = 'equipment'
    ITEM_TYPE = (
        (ACCESSORY, 'Accessory'),
        (CONSUMABLE, 'Consumable'),
        (EQUIPMENT, 'Equipment')
    )
    item_type = models.CharField(
        "Choose One",
        choices=ITEM_TYPE,
        default='equipment',
        max_length=30
    )

    def get_absolute_url(self):
        kwargs = {
            'id': self.id,
            'slug': self.slug
        }
        return reverse('item_detail_view', kwargs=kwargs)  

    def save(self, *args, **kwargs):
        if self.item_type == 'equipment':
            value = self.equipment_tag
        else:
            value = self.name
        self.slug = slugify(value, allow_unicode=True)
        super().save(*args, **kwargs)
        self.set_tag()

    def set_tag(self):
        if self.item_type == 'equipment':
            if not self.equipment_tag:
                prefix = 'SEAS'
                department_prefix = self.department.tag_prefix
                tag = prefix + department_prefix + str(self.id + (10 ** 3))            # Creates a number starting with 'SEAS' + department prefix and ending with a 4 character (10^4) unique ID
                request = Item.objects.get(id=self.id)
                request.equipment_tag = tag
                request.save()

    def __str__(self):
        return self.name

class EquipmentAccessory(models.Model):
    item = models.ForeignKey(Item,related_name='item',on_delete=models.CASCADE)
    accessory = models.ForeignKey(Item,related_name='item_accessory',on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=15,decimal_places=3)

    class Meta:
        verbose_name_plural = "Equipment Accessories"

    def __str__(self):
        return self.item.name

# class EquipmentConsumable(models.Model):
#     item = models.ForeignKey(Item,on_delete=models.CASCADE)
#     consumable = models.ForeignKey(Item,on_delete=models.CASCADE)
#     quantity = models.DecimalField(decimal_places=3)

#     def __str__(self):
#         return self.item.name