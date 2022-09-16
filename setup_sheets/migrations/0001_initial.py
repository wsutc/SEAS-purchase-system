# Generated by Django 4.0.3 on 2022-06-07 17:15

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("purchases", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Fixture",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=55, verbose_name="Fixture Name")),
                ("part_number", models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name="Material",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=30, verbose_name="Material Name")),
                (
                    "abbreviation",
                    models.CharField(
                        blank=True, max_length=10, verbose_name="Short Name"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SetupSheet",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=50, verbose_name="Setup Name")),
                ("slug", models.SlugField(default="", editable=False, max_length=255)),
                ("part_number", models.CharField(max_length=15)),
                ("part_revision", models.CharField(max_length=10)),
                ("program_name", models.CharField(max_length=30)),
                ("operation", models.CharField(max_length=30)),
                ("size", models.TextField(verbose_name="Stock Size")),
                ("created_date", models.DateTimeField(auto_now_add=True)),
                ("revision", models.CharField(max_length=2)),
                ("revision_date", models.DateField()),
                ("notes", models.TextField()),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "fixture",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="setup_sheets.fixture",
                    ),
                ),
                (
                    "material",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="setup_sheets.material",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ToolComponents",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(max_length=30, verbose_name="Component Name"),
                ),
                (
                    "product_number",
                    models.CharField(max_length=30, verbose_name="MFG Number"),
                ),
                (
                    "tool_type",
                    models.CharField(
                        choices=[
                            ("holder", "Tool/Insert Holder"),
                            ("insert", "Insert"),
                        ],
                        default="holder",
                        max_length=15,
                    ),
                ),
                (
                    "manufacturer",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="purchases.manufacturer",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Tool",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=50, verbose_name="Tool Name")),
                ("is_assembly", models.BooleanField(verbose_name="Assembly?")),
                (
                    "product_number",
                    models.CharField(
                        max_length=30, verbose_name="MFG Number (single tool)"
                    ),
                ),
                (
                    "flutes",
                    models.IntegerField(
                        validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                (
                    "default_position",
                    models.IntegerField(
                        validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                (
                    "manufacturer",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="purchases.manufacturer",
                    ),
                ),
                (
                    "tool_holder",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="holder",
                        to="setup_sheets.toolcomponents",
                    ),
                ),
                (
                    "tool_insert",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="insert",
                        to="setup_sheets.toolcomponents",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SetupSheetTool",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "position",
                    models.IntegerField(
                        validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                (
                    "setup_sheet",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="setup_sheets.setupsheet",
                    ),
                ),
                (
                    "tool",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="setup_sheets.tool",
                    ),
                ),
            ],
            options={
                "ordering": ("position",),
            },
        ),
        migrations.AddField(
            model_name="setupsheet",
            name="tools",
            field=models.ManyToManyField(
                through="setup_sheets.SetupSheetTool", to="setup_sheets.tool"
            ),
        ),
    ]
