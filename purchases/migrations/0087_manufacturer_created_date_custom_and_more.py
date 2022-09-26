# Generated by Django 4.0.3 on 2022-09-15 17:40

# from venv import create

# import django.utils.timezone
from django.db import migrations, models
from django.utils.text import slugify


def create_manufacturer_slug(apps, schema):
    Manufacturer = apps.get_model("purchases", "Manufacturer")
    qs = Manufacturer.objects.all()
    for m in qs:
        m.slug = slugify(m.name, allow_unicode=True)

    Manufacturer.objects.bulk_update(qs, ["slug"])


class Migration(migrations.Migration):

    dependencies = [
        ("purchases", "0086_manufacturer_slugger"),
    ]

    operations = [
        # migrations.AddField(
        #     model_name='manufacturer',
        #     name='created_date',
        #     field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
        #     preserve_default=False,
        # ),
        migrations.RunPython(create_manufacturer_slug),
        migrations.AlterField(
            model_name="manufacturer",
            name="slug",
            field=models.SlugField(editable=False, unique=True),
        ),
    ]