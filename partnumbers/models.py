from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from purchases.models import DocumentNumber
from web_project.models import BaseModel

# Create your models here.


class PartType(BaseModel):
    pass


class Part(BaseModel):
    number = models.CharField(
        _("part number"), max_length=25, unique=True, editable=False
    )
    type = models.ForeignKey(PartType, on_delete=models.PROTECT)

    @property
    def long_description(self) -> str:
        return f"{self.number} | {self.name}"

    class Meta:
        ordering = ["number"]

    def save(self, *args, **kwargs):
        if self._state.adding:
            doc_number, _ = DocumentNumber.objects.get_or_create(
                document="PartNumber",
                defaults={"prefix": "115", "padding_digits": "4"},
            )
            self.number = doc_number.get_next_number()
        if not self.slug:
            self.slug = slugify(self.number, allow_unicode=True)
        return super().save(*args, **kwargs)


class PartRevision(BaseModel):
    name = models.CharField(_("revision"), max_length=4, default="A")
    part = models.ForeignKey(Part, on_delete=models.CASCADE)

    @property
    def long_description(self):
        return f"{self.part.number} | Rev {self.name}"

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            slug_base = f"{self.part.number} {self.name}"
            self.slug = slugify(slug_base, allow_unicode=True)
        return super().save(*args, **kwargs)
