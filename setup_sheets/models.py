from django.conf import settings

# from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from purchases.models import Manufacturer

# Create your models here.
# class Manufacturer(models.Model):
#     name = models.CharField(max_length=50)
#     website = models.URLField()

#     def __str__(self):
#         return self.name


class BaseModel(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        related_name="%(app_label)s_%(class)s_related",
    )
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)
    slug = models.SlugField(editable=False)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.slug = slugify(self.name, allow_unicode=True)

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class ToolComponents(models.Model):
    HOLDER = "holder"
    INSERT = "insert"
    COMPONENT_TYPE = ((HOLDER, "Tool/Insert Holder"), (INSERT, "Insert"))

    name = models.CharField("Component Name", max_length=30)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.SET_NULL, null=True)
    product_number = models.CharField("MFG Number", max_length=30)
    tool_type = models.CharField(
        choices=COMPONENT_TYPE,
        default="holder",
        max_length=15,
    )

    def __str__(self):
        return self.name


class Tool(BaseModel):
    name = models.CharField("Tool Name", max_length=50)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.SET_NULL, null=True)
    is_assembly = models.BooleanField("Assembly?")
    tool_holder = models.ForeignKey(
        ToolComponents,
        on_delete=models.SET_NULL,
        null=True,
        related_name="holder",
        blank=True,
    )
    tool_insert = models.ForeignKey(
        ToolComponents,
        on_delete=models.SET_NULL,
        null=True,
        related_name="insert",
        blank=True,
    )
    product_number = models.CharField("MFG Number (single tool)", max_length=30)
    flutes = models.IntegerField(validators=[MinValueValidator(1)])
    default_position = models.IntegerField(validators=[MinValueValidator(1)])


class Fixture(models.Model):
    name = models.CharField("Fixture Name", max_length=55)
    part_number = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Material(models.Model):
    name = models.CharField("Material Name", max_length=30)
    abbreviation = models.CharField("Short Name", max_length=10, blank=True)

    def __str__(self):
        return self.name


class Part(BaseModel):
    number = models.CharField(max_length=50, unique=True)
    material = models.ForeignKey(Material, on_delete=models.PROTECT)

    class Meta:
        ordering = ["number"]

    def get_absolute_url(self):
        kwargs = {"pk": self.id, "slug": self.slug}
        return reverse("part_detail", kwargs=kwargs)

    def __str__(self) -> str:
        value = f"{self.number} | {self.name}"
        return value


class PartRevision(models.Model):
    part = models.ForeignKey(Part, on_delete=models.CASCADE)
    revision = models.CharField(max_length=10, blank=True)

    class Meta:
        ordering = ["revision"]
        get_latest_by = ["revision"]
        constraints = [
            models.UniqueConstraint(
                fields=("part", "revision"),
                name="unique_part_revision",
            ),
        ]

    def get_absolute_url(self):
        return reverse(
            "partrevision_detail",
            kwargs={
                "revision": self.revision,
                "slug": self.part.slug,
                "pk": self.part.pk,
            },
        )

    def __str__(self) -> str:
        value = "{part_number} | Rev {revision}".format(
            part_number=self.part.number,
            revision=self.revision,
        )
        return value


class SetupSheet(BaseModel):
    name = models.CharField("Setup Name", max_length=50)
    part = models.ForeignKey(Part, on_delete=models.PROTECT, null=True)
    part_revision = models.ForeignKey(
        PartRevision,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    program_name = models.CharField(max_length=30)
    operation = models.CharField(max_length=30)
    size = models.TextField("Stock Size")
    revision = models.CharField(max_length=2)
    revision_date = models.DateField(auto_now=False, auto_now_add=False)
    tools = models.ManyToManyField(Tool, through="SetupSheetTool")
    notes = models.TextField()
    fixture = models.ForeignKey(Fixture, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ["part__number", "operation"]

    def get_absolute_url(self):
        kwargs = {"pk": self.id, "slug": self.slug}
        return reverse("setup_sheet_detail_view", kwargs=kwargs)


class SetupSheetTool(models.Model):
    setup_sheet = models.ForeignKey(SetupSheet, on_delete=models.CASCADE)
    tool = models.ForeignKey(Tool, on_delete=models.CASCADE)

    position = models.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        ordering = ("position",)

    def __str__(self):
        return self.setup_sheet.name
