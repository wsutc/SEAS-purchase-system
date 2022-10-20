from model_bakery.recipe import Recipe, foreign_key

from globals.models import DefaultValue

from .models import Department, PurchaseRequest, Requisitioner, Vendor

seas_department = Recipe(
    Department,
    code="SEAS",
    name="School of Engineering and Applied Sciences",
)

sales_tax_rate_settings = Recipe(
    DefaultValue,
    name="Sales Tax Rate",
    data_type="FLOAT",
    value=0.087,
)

vendor_tormach = Recipe(
    Vendor,
    name="Tormach",
)

requisitioner_all = Recipe(
    Requisitioner,
    department=foreign_key(seas_department),
)

# default_user = Recipe(
#     auth.User
# )

default_pr = Recipe(
    PurchaseRequest,
    # requisitioner=foreign_key(requisitioner_all),
    vendor=foreign_key(vendor_tormach),
    sales_tax_rate=0.087,
)
