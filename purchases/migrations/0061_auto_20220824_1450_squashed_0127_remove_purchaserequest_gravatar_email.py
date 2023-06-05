# Generated by Django 4.0.3 on 2022-10-18 18:48

from decimal import Decimal
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.expressions
import django.utils.timezone
import djmoney.models.fields
import purchases.models.models_data
import web_project.fields

from .zerozerozeroone_first_squash import (
    CURRENCY_CHOICES,
)

from .migration_tools import (
    create_account_slugs,
    create_carrier_slugs,
    create_manufacturer_slug,
    change_account_foreign_relationship,
    populate_spendcat_ext,
)


# Functions from the following migrations need manual copying.
# Move them and any dependencies into this file, then update the
# RunPython operations to refer to the local versions:
# purchases.migrations.0061_auto_20220824_1450
# purchases.migrations.0062_alter_accounts_slug_alter_carrier_slug
# purchases.migrations.0087_manufacturer_created_date_custom_and_more
# purchases.migrations.0099_auto_20220926_1435
# purchases.migrations.0101_auto_20220926_1651


class Migration(migrations.Migration):
    dependencies = [
        # ("accounts", "0003_alter_basetransaction_amount_and_more"),
        ("purchases", "migration_tools"),
        ("accounts", "0004_spendcategory"),
    ]

    operations = [
        migrations.AddField(
            model_name="accounts",
            name="slug",
            field=models.SlugField(),
        ),
        migrations.RunPython(
            code=create_account_slugs,
        ),
        migrations.AlterField(
            model_name="accounts",
            name="slug",
            field=models.SlugField(unique=True),
        ),
        migrations.RunPython(
            code=create_carrier_slugs,
        ),
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
        migrations.AlterField(
            model_name="vendor",
            name="slug",
            field=models.SlugField(editable=False, unique=True),
        ),
        migrations.AddField(
            model_name="documentnumber",
            name="last_generated_date",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="vendor",
            name="created_date",
            field=models.DateTimeField(auto_now_add=True),
        ),
        # migrations.AlterField(
        #     model_name="purchaserequest",
        #     name="sales_tax_rate",
        #     field=models.DecimalField(
        # decimal_places=5, default=".087", max_digits=10),
        # ),
        migrations.AlterField(
            model_name="simpleproduct",
            name="unit_price",
            field=models.DecimalField(decimal_places=4, max_digits=14),
        ),
        migrations.AddField(
            model_name="tracker",
            name="active",
            field=models.BooleanField(default=True),
        ),
        migrations.CreateModel(
            name="TrackerItems",
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
                    "quantity",
                    models.DecimalField(
                        decimal_places=3,
                        max_digits=15,
                        verbose_name="quantity in shipment",
                    ),
                ),
                (
                    "missing",
                    models.BooleanField(default=False, verbose_name="missing"),
                ),
                (
                    "simple_product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="purchases.simpleproduct",
                        verbose_name="item",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="tracker",
            name="received",
            field=models.BooleanField(
                default=False, verbose_name="package received"
            ),
        ),
        migrations.AddField(
            model_name="tracker",
            name="simple_product",
            field=models.ManyToManyField(
                through="purchases.TrackerItems",
                to="purchases.simpleproduct",
                verbose_name="items",
            ),
        ),
        migrations.CreateModel(
            name="VendorOrder",
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
                ("slug", models.SlugField(editable=False, unique=True)),
                ("created_date", models.DateTimeField(auto_now_add=True)),
                (
                    "name",
                    models.CharField(
                        max_length=50, verbose_name="order number"
                    ),
                ),
                ("link", models.URLField(blank=True, verbose_name="link")),
                (
                    "purchase_requests",
                    models.ManyToManyField(
                        to="purchases.purchaserequest",
                        verbose_name="purchase_requests",
                    ),
                ),
                (
                    "vendor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="purchases.vendor",
                    ),
                ),
                (
                    "sales_tax",
                    djmoney.models.fields.MoneyField(
                        decimal_places=2,
                        default=Decimal("0"),
                        default_currency="USD",
                        max_digits=14,
                        verbose_name="sales tax",
                    ),
                ),
                (
                    "sales_tax_currency",
                    djmoney.models.fields.CurrencyField(
                        choices=CURRENCY_CHOICES,
                        default="USD",
                        editable=False,
                        max_length=3,
                    ),
                ),
                (
                    "shipping",
                    djmoney.models.fields.MoneyField(
                        decimal_places=2,
                        default=Decimal("0"),
                        default_currency="USD",
                        max_digits=14,
                        verbose_name="shipping",
                    ),
                ),
                (
                    "shipping_currency",
                    djmoney.models.fields.CurrencyField(
                        choices=CURRENCY_CHOICES,
                        default="USD",
                        editable=False,
                        max_length=3,
                    ),
                ),
                (
                    "subtotal",
                    djmoney.models.fields.MoneyField(
                        decimal_places=2,
                        default=Decimal("0"),
                        default_currency="USD",
                        max_digits=14,
                        verbose_name="subtotal",
                    ),
                ),
                (
                    "subtotal_currency",
                    djmoney.models.fields.CurrencyField(
                        choices=CURRENCY_CHOICES,
                        default="USD",
                        editable=False,
                        max_length=3,
                    ),
                ),
                (
                    "invoice_due_date",
                    models.DateField(
                        blank=True, null=True, verbose_name="invoice due date"
                    ),
                ),
                (
                    "invoice_number",
                    models.CharField(
                        blank=True,
                        max_length=50,
                        verbose_name="invoice number",
                    ),
                ),
                (
                    "order_placed",
                    models.DateField(
                        blank=True, verbose_name="date order placed"
                    ),
                ),
            ],
            options={
                "verbose_name": "vendor order",
                "verbose_name_plural": "vendor orders",
                "ordering": ["-order_placed", "-created_date"],
            },
        ),
        migrations.AddField(
            model_name="trackeritems",
            name="tracker",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="purchases.tracker",
                verbose_name="tracker",
            ),
        ),
        migrations.RenameModel(
            old_name="TrackerItems",
            new_name="TrackerItem",
        ),
        migrations.CreateModel(
            name="AccountGroup",
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
                ("slug", models.SlugField(editable=False, unique=True)),
                ("created_date", models.DateTimeField(auto_now_add=True)),
                (
                    "name",
                    models.CharField(
                        max_length=50, unique=True, verbose_name="group name"
                    ),
                ),
                (
                    "accounts",
                    models.ManyToManyField(
                        to="purchases.accounts", verbose_name="accounts"
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "account groups",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="TrackerStatusSteps",
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
                    "tracker_status",
                    models.CharField(max_length=50, verbose_name="status"),
                ),
                (
                    "rank",
                    models.PositiveSmallIntegerField(
                        help_text="rank in sort order",
                        unique=True,
                        verbose_name="rank",
                    ),
                ),
            ],
        ),
        migrations.AlterField(
            model_name="purchaserequest",
            name="purchase_type",
            field=models.CharField(
                choices=[
                    ("po", "PURCHASE ORDER"),
                    ("pcard", "PCARD"),
                    ("iri", "IRI"),
                    ("invoice voucher", "INVOICE VOUCHER"),
                    ("contract", "CONTRACT"),
                ],
                default="pcard",
                max_length=25,
                verbose_name="Choose One",
            ),
        ),
        migrations.AlterField(
            model_name="purchaserequest",
            name="status",
            field=models.CharField(
                choices=[
                    ("0", "created"),
                    ("1", "awaiting approval"),
                    ("2", "approved"),
                    ("3", "complete"),
                    ("4", "denied (no resubmission)"),
                    ("5", "returned (please resubmit"),
                    ("6", "ordered"),
                    ("7", "shipped"),
                    ("8", "received"),
                    ("9", "partial"),
                ],
                default="0",
                max_length=150,
            ),
        ),
        migrations.RemoveField(
            model_name="accounts",
            name="fund",
        ),
        migrations.AlterField(
            model_name="accounts",
            name="account",
            field=models.CharField(
                help_text="in form XXXX-XXXX.",
                max_length=10,
                verbose_name="account",
            ),
        ),
        migrations.AlterField(
            model_name="accounts",
            name="account_title",
            field=models.CharField(
                help_text="human-readable description of account",
                max_length=200,
                verbose_name="account title",
            ),
        ),
        migrations.AlterField(
            model_name="accounts",
            name="budget_code",
            field=models.CharField(
                help_text="usually first four characters of account",
                max_length=5,
                verbose_name="budget code",
            ),
        ),
        migrations.AlterField(
            model_name="accounts",
            name="program_workday",
            field=models.CharField(
                blank=True, max_length=10, verbose_name="program workday"
            ),
        ),
        migrations.AlterField(
            model_name="purchaserequest",
            name="status",
            field=models.CharField(
                choices=[
                    ("0", "created"),
                    ("1", "awaiting approval"),
                    ("2", "approved"),
                    ("6", "ordered"),
                    ("7", "shipped"),
                    ("9", "partial"),
                    ("8", "received"),
                    ("3", "complete"),
                    ("4", "denied (no resubmission)"),
                    ("5", "returned (please resubmit"),
                ],
                default="0",
                max_length=150,
            ),
        ),
        migrations.AlterField(
            model_name="accounts",
            name="account",
            field=models.CharField(
                help_text="in form XXXX-XXXX.",
                max_length=10,
                verbose_name="account",
            ),
        ),
        migrations.AddField(
            model_name="accounts",
            name="slug",
            field=models.SlugField(),
        ),
        migrations.AlterField(
            model_name="accounts",
            name="account",
            field=models.CharField(
                help_text="in form XXXX-XXXX.",
                max_length=10,
                verbose_name="account",
            ),
        ),
        migrations.AddField(
            model_name="accounts",
            name="created_date",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name="Status",
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
                ("name", models.CharField(max_length=50)),
                (
                    "rank",
                    models.PositiveSmallIntegerField(
                        editable=False, verbose_name="rank"
                    ),
                ),
                (
                    "model",
                    models.CharField(
                        choices=[("PR", "Purchase Request"), ("OR", "Order")],
                        max_length=30,
                        verbose_name="model",
                    ),
                ),
            ],
            options={
                "verbose_name": "status",
                "verbose_name_plural": "statuses",
                "ordering": ["rank"],
            },
        ),
        migrations.AddConstraint(
            model_name="status",
            constraint=models.UniqueConstraint(
                django.db.models.expressions.F("model"),
                django.db.models.expressions.F("rank"),
                name="status_model_unique",
            ),
        ),
        migrations.RemoveConstraint(
            model_name="status",
            name="status_model_unique",
        ),
        migrations.AddConstraint(
            model_name="status",
            constraint=models.UniqueConstraint(
                fields=("model", "rank"), name="status_model_unique"
            ),
        ),
        migrations.AlterModelOptions(
            name="status",
            options={
                "ordering": ["parent_model", "rank"],
                "verbose_name": "status",
                "verbose_name_plural": "statuses",
            },
        ),
        migrations.RemoveConstraint(
            model_name="status",
            name="status_model_unique",
        ),
        migrations.RenameField(
            model_name="status",
            old_name="model",
            new_name="parent_model",
        ),
        migrations.AddConstraint(
            model_name="status",
            constraint=models.UniqueConstraint(
                fields=("parent_model", "rank"), name="status_model_unique"
            ),
        ),
        migrations.RemoveField(
            model_name="purchaserequest",
            name="status",
        ),
        migrations.AddField(
            model_name="status",
            name="open",
            field=models.BooleanField(
                default=False,
                help_text="purchase request not complete",
                verbose_name="open",
            ),
        ),
        migrations.AddField(
            model_name="purchaserequest",
            name="status",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="purchases.status",
            ),
        ),
        migrations.AlterField(
            model_name="manufacturer",
            name="slug",
            field=models.SlugField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.RunPython(
            code=create_manufacturer_slug,  # noqa: E501
        ),
        migrations.AlterField(
            model_name="manufacturer",
            name="slug",
            field=models.SlugField(editable=False, unique=True),
        ),
        migrations.RemoveField(
            model_name="trackeritem",
            name="simple_product",
        ),
        migrations.RemoveField(
            model_name="trackeritem",
            name="tracker",
        ),
        migrations.RemoveField(
            model_name="tracker",
            name="simple_product",
        ),
        migrations.AddConstraint(
            model_name="accounts",
            constraint=models.UniqueConstraint(
                django.db.models.expressions.F("gift"),
                django.db.models.expressions.F("grant"),
                django.db.models.expressions.F("program_workday"),
                name="unique_program",
            ),
        ),
        migrations.AddConstraint(
            model_name="accounts",
            constraint=models.UniqueConstraint(
                django.db.models.expressions.F("account"),
                name="unique_account",
            ),
        ),
        migrations.DeleteModel(
            name="TrackerItem",
        ),
        migrations.AddField(
            model_name="simpleproduct",
            name="rank",
            field=models.SmallIntegerField(
                editable=False, null=True, verbose_name="in pr ordering"
            ),
        ),
        migrations.AlterField(
            model_name="vendor",
            name="discount_percentage",
            field=web_project.fields.SimplePercentageField(
                decimal_places=0, default=0, max_digits=15
            ),
        ),
        migrations.AlterField(
            model_name="vendor",
            name="discount_percentage",
            field=web_project.fields.SimplePercentageField(
                decimal_places=4, default=0, max_digits=15
            ),
        ),
        migrations.AlterField(
            model_name="vendor",
            name="discount_percentage",
            field=models.DecimalField(
                decimal_places=2, default=0, max_digits=15
            ),
        ),
        migrations.AlterField(
            model_name="vendor",
            name="discount_percentage",
            field=web_project.fields.SimplePercentageField(
                decimal_places=4, default=0, max_digits=15
            ),
        ),
        migrations.CreateModel(
            name="PurchaseRequestAccount",
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
                    "distribution_type",
                    models.CharField(
                        choices=[("P", "Percent"), ("A", "Amount")],
                        default="P",
                        max_length=1,
                    ),
                ),
                ("distribution_input", models.FloatField(default=100)),
                (
                    "account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="accounts.account",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "purchase request accounts",
            },
        ),
        migrations.AddField(
            model_name="purchaserequest",
            name="accounts_external",
            field=models.ManyToManyField(
                through="purchases.PurchaseRequestAccount",
                to="accounts.account",
            ),
        ),
        migrations.AddField(
            model_name="purchaserequestaccount",
            name="purchase_request",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="purchases.purchaserequest",
            ),
        ),
        migrations.AddField(
            model_name="purchaserequestaccount",
            name="spend_category",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="purchases.spendcategory",
            ),
        ),
        migrations.AlterField(
            model_name="purchaserequest",
            name="instruction",
            field=models.TextField(verbose_name="Special Instructions"),
        ),
        # migrations.AlterField(
        #     model_name="purchaserequest",
        #     name="sales_tax_rate",
        #     field=web_project.fields.SimplePercentageField(
        #         decimal_places=6, max_digits=10
        #     ),
        # ),
        # migrations.AlterField(
        #     model_name="purchaserequest",
        #     name="sales_tax_rate",
        #     field=models.FloatField(),
        # ),
        # migrations.AlterField(
        #     model_name="purchaserequest",
        #     name="sales_tax_rate",
        #     field=models.DecimalField(decimal_places=5, max_digits=10),
        # ),
        migrations.RunPython(
            code=change_account_foreign_relationship,  # noqa: E501
        ),
        migrations.AddField(
            model_name="purchaserequestaccount",
            name="spend_category_ext",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="accounts.spendcategory",
            ),
        ),
        migrations.RunPython(
            code=populate_spendcat_ext,
        ),
        migrations.RemoveField(
            model_name="purchaserequest",
            name="accounts",
        ),
        migrations.AlterField(
            model_name="purchaserequestaccount",
            name="spend_category_ext",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                to="accounts.spendcategory",
            ),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name="purchaserequestaccount",
            name="spend_category",
        ),
        migrations.RenameField(
            model_name="purchaserequest",
            old_name="accounts_external",
            new_name="accounts",
        ),
        migrations.AlterField(
            model_name="purchaserequestaccount",
            name="account",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="accounts.account",
                verbose_name="account",
            ),
        ),
        migrations.AlterField(
            model_name="purchaserequestaccount",
            name="spend_category_ext",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="accounts.spendcategory",
                verbose_name="spend category",
            ),
        ),
        migrations.DeleteModel(
            name="PurchaseRequestAccounts",
        ),
        # migrations.AlterField(
        #     model_name="purchaserequest",
        #     name="sales_tax_rate",
        #     field=web_project.fields.SimplePercentageField(
        #         decimal_places=9, max_digits=10
        #     ),
        # ),
        # migrations.AlterField(
        #     model_name="purchaserequest",
        #     name="sales_tax_rate",
        #     field=web_project.fields.SimplePercentageField(
        #         decimal_places=6, max_digits=10
        #     ),
        # ),
        # migrations.AlterField(
        #     model_name="purchaserequest",
        #     name="sales_tax_rate",
        #     field=web_project.fields.SimplePercentageField(
        #         decimal_places=6, max_digits=10
        #     ),
        # ),
        migrations.AddField(
            model_name="simpleproduct",
            name="taxable",
            field=models.BooleanField(default=True, verbose_name="taxable"),
        ),
        # migrations.AlterField(
        #     model_name="purchaserequest",
        #     name="sales_tax_rate",
        #     field=web_project.fields.SimplePercentageField(
        #         decimal_places=6, max_digits=10
        #     ),
        # ),
        # migrations.AlterField(
        #     model_name="purchaserequest",
        #     name="sales_tax_rate",
        #     field=web_project.fields.SimplePercentageField(
        #         decimal_places=6, max_digits=10
        #     ),
        # ),
        # migrations.AlterField(
        #     model_name="purchaserequest",
        #     name="sales_tax_rate",
        #     field=web_project.fields.SimplePercentageField(
        #         decimal_places=6, max_digits=10
        #     ),
        # ),
        # migrations.AlterField(
        #     model_name="purchaserequest",
        #     name="sales_tax_rate",
        #     field=web_project.fields.SimplePercentageField(
        #         decimal_places=6, max_digits=10
        #     ),
        # ),
        # migrations.AlterField(
        #     model_name="purchaserequest",
        #     name="sales_tax_rate",
        #     field=web_project.fields.SimplePercentageField(
        #         decimal_places=2, max_digits=10
        #     ),
        # ),
        migrations.AlterField(
            model_name="vendor",
            name="discount_percentage",
            field=web_project.fields.SimplePercentageField(
                decimal_places=2, max_digits=15
            ),
        ),
        migrations.AlterField(
            model_name="purchaserequest",
            name="sales_tax_rate",
            field=web_project.fields.SimplePercentageField(
                decimal_places=4, max_digits=10
            ),
        ),
        migrations.AddField(
            model_name="purchaserequest",
            name="new_st",
            field=models.DecimalField(
                decimal_places=4,
                default=0.087,
                max_digits=10,
                verbose_name="sales tax rate",
            ),
        ),
        migrations.AlterField(
            model_name="vendor",
            name="discount_percentage",
            field=web_project.fields.SimplePercentageField(
                decimal_places=2, default=0, max_digits=15
            ),
        ),
        # migrations.AddField(
        #     model_name="purchaserequest",
        #     name="sales_tax_rate",
        #     field=web_project.fields.SimplePercentageField(
        #         decimal_places=4,
        #         max_digits=10,
        #         null=True,
        #         verbose_name="sales tax rate",
        #     ),
        # ),
        migrations.AddField(
            model_name="vendororder",
            name="approved_request",
            field=models.FileField(
                blank=True,
                help_text="pdf",
                upload_to=purchases.models.models_data.vendor_order_attachments_path,
                validators=[
                    django.core.validators.FileExtensionValidator(
                        ["pdf", "pdfa"]
                    )
                ],
                verbose_name="approved purchase request",
            ),
        ),
    ]
