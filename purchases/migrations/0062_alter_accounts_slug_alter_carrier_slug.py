# Generated by Django 4.0.3 on 2022-08-24 22:02

import random
import string

from django.db import migrations, models
from django.utils.text import slugify


def create_slugs(apps, app_name, model_name):
    print_string = []
    model = apps.get_model(app_name, model_name)
    print_string.append(f"\nModel: {model}")
    objects = model.objects.all()
    print_string.append(
        f"First object: {objects.first()} | Total Objects: {len(objects)}"
    )
    print(print_string)
    for counter, object in enumerate(objects):
        obj_print_str = [f"Object[{counter}]: {object}"]
        if hasattr(object, "name") and object.name:
            slug_raw = f"{object.name}"
            obj_print_str.append(f"name -> {slug_raw}")
        elif hasattr(object, "program_workday") and object.program_workday:
            slug_raw = f"{object.program_workday}"
            obj_print_str.append(f"program_workday -> {slug_raw}")
        elif hasattr(object, "grant") and object.grant:
            slug_raw = f"{object.grant}"
            obj_print_str.append(f"grant -> {slug_raw}")
        elif hasattr(object, "gift") and object.gift:
            slug_raw = f"{object.gift}"
            obj_print_str.append(f"gift -> {slug_raw}")
        elif hasattr(object, "description") and object.description:
            slug_raw = f"{object.description}"
            obj_print_str.append(f"description -> {slug_raw}")
        else:
            slug_raw = random.choices(string.ascii_lowercase + string.digits, k=8)
            obj_print_str.append(f"random -> {slug_raw}")

        object.slug = slugify(slug_raw, allow_unicode=True)
        obj_print_str.append(f"-> {object.slug}")
        print(obj_print_str)

    return model, objects


def create_carrier_slugs(apps, schema_editor):
    model, objects = create_slugs(apps, "purchases", "Carrier")

    count = model.objects.bulk_update(objects, ["slug"], 100)
    print(f"{count} carriers got a slug!")


class Migration(migrations.Migration):

    dependencies = [
        ("purchases", "0061_auto_20220824_1450"),
    ]

    operations = [
        migrations.RunPython(create_carrier_slugs),
        migrations.AlterField(
            model_name="accounts",
            name="slug",
            field=models.SlugField(editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name="carrier",
            name="slug",
            field=models.SlugField(editable=False, unique=True),
        ),
    ]
