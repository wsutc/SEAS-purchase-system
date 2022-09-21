from django.db import models
from django.utils.text import slugify


class BaseModel(models.Model):
    """Base model for standardization. Includes generating slug."""

    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, editable=False)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)
