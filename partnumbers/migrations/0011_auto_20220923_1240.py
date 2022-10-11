# Generated by Django 4.0.3 on 2022-09-23 19:40

from django.db import migrations
from django.db.models import F, OuterRef, Subquery
from django.db.models.functions import Concat

# from django.utils.text import slugify


def correct_revision_slug(apps, schema_editor):
    PartRevision = apps.get_model("partnumbers", "partrevision")
    Part = apps.get_model("partnumbers", "part")

    partref = Part.objects.filter(pk=OuterRef("part"))

    PartRevision.objects.annotate(
        part_name = Subquery(partref.values('name')[:1])
    ).update(
        slug = Concat("part_name", F("name"))
    )
    part1 = PartRevision.objects.all().first()
    print(f"{part1.slug}")


class Migration(migrations.Migration):

    dependencies = [
        ("partnumbers", '0010_auto_20220923_1235'),
    ]

    operations = [
        migrations.RunPython(correct_revision_slug),
    ]
