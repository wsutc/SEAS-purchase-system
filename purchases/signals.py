# import http.client, json
# from django.conf import settings
# from django.apps import apps
from django.contrib.auth.models import User
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from purchases.vendor_linking import link_from_identifier
from web_project.helpers import first_true  # , get_app_name

from .models import (  # PurchaseRequest,; PurchaseRequestAccount,
    Accounts,
    Department,
    Requisitioner,
    SimpleProduct,
    Status,
)


def single_true(iterable) -> bool:
    """Return `True` if one and only one truthy value is present, else `False`."""
    i = iter(iterable)
    # Two things to know to understand the next line:
    # 1. an iterable will be 'consumed' as it is iterated over
    # 2. the return statement will be solved left --> right
    # So, the first `any(i)` will search for the first 'truthy' option, consuming
    # `i` as it does, and then will stop. Once that's done, the `not any(i)` starts
    # and consumes `i` unless and until it hits another 'truthy' instance. If that
    # happens, there's more than one.
    return any(i) and not any(i)


def n_trues(iterable, n: int) -> bool:
    i = iter(iterable)
    return all(any(i) for j in range(n)) and not any(i)


@receiver(pre_save, sender=Accounts)
def validate_account_program(sender, instance, **kwargs):
    if single_true(instance.identity_list):
        return first_true(instance.identity_list)


@receiver(post_save, sender=User)
def create_requisitioner(sender, instance, created, **kwargs):
    if created:
        department, _ = Department.objects.get_or_create(
            code="SEAS", defaults={"name": "School of Engineering and Applied Sciences"}
        )
        Requisitioner.objects.create(user=instance, department=department)
    instance.requisitioner.save()


# @receiver(post_save, sender=User)
# def save_requisitioner(sender, instance, **kwargs):
#     instance.requisitioner.save()


@receiver(pre_save, sender=SimpleProduct)
def create_link(sender, instance, **kwargs):
    if not instance.link:
        instance.link = link_from_identifier(
            instance.identifier, instance.purchase_request.vendor
        )


@receiver(post_delete, sender=Status)
def re_normalize_ranks(sender, instance, **kwargs):
    sender.objects.normalize_ranks("parent_model", instance.__class__)


# @receiver(post_save, sender=PurchaseRequest)
# def create_account_transaction(sender, instance, created, **kwargs):
#     # account_model = apps.get_model("accounts", "account")
#     instance_accounts = instance.accounts.all()
#     total_amount = instance.grand_total

#     def input(account):
#         return account.distribution_input

#     def input_type(account):
#         return account.distribution_type

#     dist_type = PurchaseRequestAccount.DistributionType

#     for account in instance_accounts:
#         purchaserequestaccount = instance.purchaserequestaccount_set.get(
#             account=account
#         )
#         account_share = (
#             input(purchaserequestaccount)
#             if input_type(purchaserequestaccount) == dist_type.AMOUNT
#             else input(purchaserequestaccount) * total_amount
#         )
#         # account_obj = account_model.objects.get(account=account.account)
#         _ = account.transact(amount=account_share, purchase_request=instance)


# @receiver(pre_save, sender=Tracker)
# def get_tracker(sender, instance, *args, **kwargs):
#     if not instance.id:
#         instance.id = instance.tracking_number
#         n,c,m,r = tracking.register_tracker(
#                       instance.tracking_number,
#                       instance.carrier
#                   )

#         if r:
#             instance.carrier = c
#             instance.tracking_number = n
#         else:
#             raise KeyError('No valid trackers created. /
#                       Is the tracker already registered?')

# api_key = settings.SHIP24_KEY

# conn = http.client.HTTPSConnection("api.ship24.com")
# headers = {
#     'Content-Type': "application/json",
#     'Authorization': "Bearer " + api_key
# }

# if instance.carrier:
#     carrier_slug = instance.carrier.slug
# else:
#     carrier_slug = None
# tracking_number = instance.tracking_number

# payload = build_payload(tracking_number, carrier_slug)

# conn.request("POST", "/public/v1/trackers", payload, headers)

# response = conn.getresponse()
# data = response.read()
# dataJson = json.loads(data.decode("utf-8"))

# tracking = dataJson['data']['tracker']

# if str(response.status).startswith('2'):
#     instance.id = tracking['trackerId']
#     instance.tracking_number = tracking['trackingNumber']
#     # instance.events = dataJson.get('events')

# @receiver(post_save, sender=PurchaseRequest)
# def update_tracker(sender, instance, *args, **kwargs):
#     if tracker := instance.tracker:
#         Tracker.update(tracker)


# @receiver(post_save, sender=PurchaseRequest)
# def add_to_smartsheet(sender, instance, *args, **kwargs):
#     data = [
#         {
#             "Status": "Submitted",
#             "First Name": instance.requisitioner.user.first_name,
#             "Last Name": instance.requisitioner.user.last_name,
#             "Requestor": instance.requisitioner.user.email,
#             "Requestor WSU ID#": "sometext1",
#         }
#     ]
