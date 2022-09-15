from django.db.models.signals import post_save, pre_save, post_delete
from django.contrib.auth.models import User
from django.dispatch import receiver

# import http.client, json
# from django.conf import settings
from django.contrib.auth.models import User

from purchases.vendor_linking import link_from_identifier

from .models import (
    Accounts,
    Department,
    Status,
    Requisitioner,
    PurchaseRequest,
    SimpleProduct,
)

from web_project.helpers import first_true

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
def validate_account_program(sender, instance, created, **kwargs):
    if single_true(instance.identity_list):
        return first_true(instance.identity_list)


@receiver(post_save, sender=User)
def create_requisitioner(sender, instance, created, **kwargs):
    if created:
        department = Department.objects.get(code="SEAS")
        Requisitioner.objects.create(user=instance, department=department)


@receiver(post_save, sender=User)
def save_requisitioner(sender, instance, **kwargs):
    instance.requisitioner.save()


@receiver(pre_save, sender=SimpleProduct)
def create_link(sender, instance, **kwargs):
    if not instance.link:
        instance.link = link_from_identifier(
            instance.identifier, instance.purchase_request.vendor
        )


@receiver(post_delete, sender=Status)
def re_normalize_ranks(sender, instance, **kwargs):
    sender.objects.normalize_ranks("parent_model", instance.__class__)


# @receiver(post_save, sender=Tracker)
# def post_save_tracker_update(sender, instance, created, **kwargs):
#     # webhook = kwargs.get('webhook',None)

#     # updating = instance.getattr('_updating',False)

#     # if updating:
#     #     return

#     # tracker = Tracker.objects.get(id=instance.id)
#     response = update_tracking_details(instance.tracking_number, instance.carrier.carrier_code)

#     if response.get('code') == 0:
#         status = response.get('status')
#         sub_status = response.get('sub_status')
#         delivery_estimate = response.get('delivery_estimate')
#         events = response.get('events')
#         events_hash = response.get('events_hash')

#         fields = {
#             'status': status,
#             'sub_status': sub_status,
#             'delivery_estimate': delivery_estimate,
#             'events': events,
#             'events_hash': events_hash
#         }

#         update_tracker_fields(instance,fields)

# instance_changed = False

# update_fields = []

# # Update values on Tracker
# # update_fields.extend( ['status'] if instance.status != status else [])
# update_fields.extend( ['sub_status'] if instance.sub_status != sub_status else [])
# update_fields.extend( ['delivery_estimate'] if instance.delivery_estimate != delivery_estimate else [])

# instance.status = status
# instance.sub_status = sub_status
# instance.delivery_estimate = delivery_estimate

# if str(events_hash) != instance.events_hash:
#     _, _ = create_events(instance,instance.events)

#     update_fields.extend( ['events'] if instance.events != events else [])
#     update_fields.extend( ['events_hash'] if instance.events_hash != events_hash else [])

#     instance.events = events
#     instance.events_hash = events_hash
#     # instance_changed = True

# if len(update_fields) > 0:
#     instance.save(update_fields=update_fields)


# @receiver(pre_save, sender=Tracker)
# def get_tracker(sender, instance, *args, **kwargs):
#     if not instance.id:
#         instance.id = instance.tracking_number
#         n,c,m,r = tracking.register_tracker(instance.tracking_number, instance.carrier)

#         if r:
#             instance.carrier = c
#             instance.tracking_number = n
#         else:
#             raise KeyError('No valid trackers created. Is the tracker already registered?')

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

# @receiver(pre_save, sender=PurchaseRequest)
# def create_tracker(sender, instance, *args, **kwargs):
#     if not instance.tracker and instance.tracking_number:               # if tracking number but no tracker; suggests that it has just been added
#         carrier = instance.carrier
#         tracking_number = instance.tracking_number

#         try:
#             tracker, _ = Tracker.objects.get_or_create(carrier=carrier,tracking_number=tracking_number)
#             # tracker.id = tracker.tracking_number
#             # tracker.save()
#             # tracker = Tracker.objects.get(id=tracker.id)
#             instance.tracker = tracker
#             # Tracker.update(tracker[0])
#             # return True
#         except KeyError as err:
#             print(err)
#     # return False

# @receiver(post_save, sender=PurchaseRequest)
# def update_tracker(sender, instance, *args, **kwargs):
#     if tracker := instance.tracker:
#         Tracker.update(tracker)


@receiver(post_save, sender=PurchaseRequest)
def add_to_smartsheet(sender, instance, *args, **kwargs):
    data = [
        {
            "Status": "Submitted",
            "First Name": instance.requisitioner.user.first_name,
            "Last Name": instance.requisitioner.user.last_name,
            "Requestor": instance.requisitioner.user.email,
            "Requestor WSU ID#": "sometext1",
        }
    ]
