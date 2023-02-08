from django.conf import settings
from django.db import models
from django.db.models import Max  # Count, F,
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from purchases.models import DocumentNumber, RankManager
from web_project.models import BaseModel


# Create your models here.
class Project(BaseModel):
    number = models.CharField(max_length=10, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        verbose_name=_("created by"),
        related_name="+",
        editable=False,
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        verbose_name=_("updated by"),
        related_name="+",
        editable=False,
    )
    updated_date = models.DateTimeField(
        _("updated datetime"), auto_now=True, editable=False
    )
    manager = models.ForeignKey(
        "purchases.Requisitioner",
        verbose_name=_("project manager"),
        on_delete=models.PROTECT,
    )
    purchase_requests = models.ManyToManyField(
        "purchases.PurchaseRequest",
        verbose_name=_("purchase requests"),
        through="projects.ProjectPurchaseRequest",
        blank=True,
    )

    def save(self, *args, **kwargs):
        if not self.number:
            doc_number, _ = DocumentNumber.objects.get_or_create(
                document="Project",
                defaults={
                    "prefix": "PJ",
                    "padding_digits": 4,
                },
            )
            self.number = doc_number.get_next_number()
        if not self.slug:
            self.slug = slugify(self.number, allow_unicode=True)

        # if not self.created_by:
        #     self.created_by =

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        kwargs = {"slug": self.slug}
        return reverse("detail_project", kwargs=kwargs)


class ProjectPurchaseRequest(models.Model):
    rank = models.SmallIntegerField(_("in project ordering"), editable=False)
    project = models.ForeignKey(
        "projects.Project", verbose_name=_("project"), on_delete=models.CASCADE
    )
    purchase_request = models.ForeignKey(
        "purchases.PurchaseRequest",
        verbose_name=_("purchase request"),
        on_delete=models.CASCADE,
    )

    # objects = RankManager()

    def save(self, *args, **kwargs):
        if not self.rank:
            self.rank = self.get_next_rank()

        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        _ = super().delete(*args, **kwargs)

        self.__class__.objects.normalize_ranks("parent_model")

    def get_next_rank(self):
        results = self.__class__.objects.aggregate(Max("rank"))

        current_order = results["rank__max"]
        current_order = current_order if current_order else 0

        value = current_order + 1
        return value
