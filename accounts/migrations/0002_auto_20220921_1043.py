# Generated by Django 4.0.3 on 2022-09-21 17:43

from django.db import migrations, models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from web_project.helpers import first_true


def copy_account_to_accounts(apps, schema_editor):
    Purchases_Accounts = apps.get_model("purchases", "Accounts")
    Account = apps.get_model("accounts", "Account")

    old_accounts = Purchases_Accounts.objects.all()
    count = len(old_accounts)
    print(f"{count} accounts found to migrate.")

    MATCH = {
        "program_workday": "PG",
        "grant": "GR",
        "gift": "GF",
    }

    IDENTITY_LIST = ["program_workday", "grant", "gift"]

    def which_fund(obj: object):
        for attr in IDENTITY_LIST:
            if getattr(obj, attr):
                code = MATCH[attr]
                # type = Account.FundType(code)

                return code

    def get_identity(obj: object):
        value_list = [getattr(obj, x) for x in IDENTITY_LIST]
        value = first_true(value_list, False)
        return value

    created_count = 0
    for account in old_accounts:
        fund_type = which_fund(account)
        fund = get_identity(account)
        slug = slugify(fund)

        if not fund_type or not fund:
            raise KeyError("Error finding fund type or identity.")

        account_new, created = Account.objects.update_or_create(
            fund = fund,
            defaults = {
                "name": account.account_title,
                "cost_center": account.cost_center,
                "fund_type": fund_type,
                "account": account.account,
                "budget_code": account.budget_code,
                "starting_balance": 0,
                "starting_balance_datetime": timezone.now(),
                "current_balance": 0,
                "changed_datetime": timezone.now(),
                "in_use": True,
                "slug": slug,
            }
        )

        if created:
            created_count += 1
            print(f"Account '{account_new.name}' created. Fund type: {account_new.fund_type}")
        else:
            print(f"Account '{account_new.name}' already existed.")

    print(f"{created_count} accounts created successfully.")


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('purchases', '0089_delete_transaction'),
    ]

    operations = [
        migrations.AlterField(
            model_name = "account",
            name = "account",
            field = models.CharField(_("account"), help_text=_("in form XXXX-XXXX."), max_length=10, unique=False),
        ),
        migrations.RunPython(copy_account_to_accounts),
    ]
