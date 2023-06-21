# from django.contrib.auth.models import User
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


# Create your models here.
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


class Manufacturer(BaseModel):
    website = models.URLField(blank=True, null=True)

    def get_absolute_url(self):
        return reverse("manufacturer_detail", kwargs={"pk": self.pk, "slug": self.slug})


class Grade(BaseModel):
    abbreviation = models.CharField(max_length=15)
    description = models.TextField(
        help_text="Best applications, further explanation, etc.",
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ["abbreviation"]

    def save(self, *args, **kwargs) -> None:
        if self._state.adding:
            slug = slugify(self.abbreviation, allow_unicode=True)

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        string = f"{self.abbreviation} - {self.name}"
        return string


class Coating(BaseModel):
    abbreviation = models.CharField(max_length=15)
    description = models.TextField(
        help_text="Best applications, further explanation, etc.",
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ["abbreviation"]

    def save(self, *args, **kwargs) -> None:
        if self._state.adding:
            slug = slugify(self.abbreviation, allow_unicode=True)

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        string = f"{self.abbreviation} - {self.name}"
        return string


class Shape(BaseModel):
    designation = models.CharField(help_text="e.g. 'T' for \"Triangle\"", max_length=20)

    class Meta:
        ordering = ["name", "designation"]
        constraints = [
            models.UniqueConstraint(
                fields=("name", "designation"),
                name="unique_insert_shape",
            ),
        ]

    def save(self, *args, **kwargs) -> None:
        if self._state.adding:
            slug = f"{self.designation}-{self.name}"
            slug = slugify(slug, allow_unicode=True)

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        string = f"{self.designation} - {self.name}"
        return string


class Tool(BaseModel):
    name = None
    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    part_number = models.CharField(
        help_text="Manufacturer or Vendor Number",
        max_length=50,
        blank=True,
    )
    description = models.CharField(max_length=100, blank=False)
    website = models.URLField(blank=True, null=True)

    class Meta:
        ordering = ["part_number"]
        constraints = [
            models.UniqueConstraint(
                fields=("manufacturer", "part_number"),
                name="unique_tool",
            ),
        ]

    def get_absolute_url(self):
        return reverse("tool_detail", kwargs={"pk": self.pk, "slug": self.slug})

    def save(self, *args, **kwargs) -> None:
        if self._state.adding:
            slug = slugify(self.description, allow_unicode=True)

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        string = self.description
        return string


class Holder(Tool):
    designation = models.CharField(
        help_text="e.g. SER0500H11",
        max_length=50,
        unique=True,
    )

    MACHINE_TYPE_CHOICES = [
        (
            "Milling",
            (
                ("any_vertical", "Vertical Mill (CNC or Manual)"),
                ("any", "Any Mill (Vertical or Horizontal"),
                ("vertical_mill", "Vertical Mill - Manual"),
                ("horizontal_mill", "Horizontal Mill"),
                ("vertical_machining_center", "Vertical Machining Center - CNC"),
            ),
        ),
        (
            "Turning",
            (
                ("any_cnc", "Any CNC"),
                ("any", "Any Lathe"),
                ("engine_lathe", "Engine Lathe - Manual"),
                ("slant_bed_cnc", "Slant Bed - CNC"),
            ),
        ),
    ]
    machine_type = models.CharField(
        max_length=30,
        choices=MACHINE_TYPE_CHOICES,
        default="any_vertical",
    )

    class Meta:
        ordering = ["designation", "description"]

    def save(self, *args, **kwargs) -> None:
        if self._state.adding:
            if designation := self.designation:
                slug = slugify(designation, allow_unicode=True)
            else:
                slug = slugify(self.description, allow_unicode=True)

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        string = self.description
        return string


class Insert(Tool):
    package_quantity = models.IntegerField(blank=True, null=True)
    designation = models.CharField(help_text="e.g. 11IRA60", max_length=50, unique=True)
    holder = models.ManyToManyField(Holder)
    size = models.CharField(max_length=30, blank=True, null=True)
    thickness = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        blank=True,
        null=True,
    )
    application = models.CharField(
        help_text="Internal/External/etc.",
        max_length=50,
        blank=True,
        null=True,
    )
    shape = models.ForeignKey(Shape, on_delete=models.PROTECT, blank=True, null=True)
    hand = models.CharField(
        help_text="Left/Right/Neutral",
        max_length=15,
        blank=True,
        null=True,
    )
    corner_radius = models.CharField(max_length=15, blank=True, null=True)
    grade = models.ForeignKey(Grade, on_delete=models.PROTECT, blank=True, null=True)
    coating = models.ForeignKey(
        Coating,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    miscellaneous = models.TextField(
        help_text="e.g. pitch range, finish, preferred application",
        blank=True,
        null=True,
    )

    def save(self, *args, **kwargs) -> None:
        if self._state.adding:
            if designation := self.designation:
                slug = slugify(designation, allow_unicode=True)
            else:
                slug = slugify(self.description, allow_unicode=True)

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        string = self.description
        return string
