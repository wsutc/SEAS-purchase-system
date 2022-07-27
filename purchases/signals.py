from django.db.models.signals import post_save, pre_save
from django.contrib.auth.models import User
from django.dispatch import receiver
import http.client, json
from django.conf import settings
from django.contrib.auth.models import User

from .models.models_metadata import Department
from .models.models_apis import Tracker, create_events
from .models.models_data import Requisitioner, PurchaseRequest

from .tracking import build_payload, update_tracking_details
from purchases import tracking

@receiver(post_save, sender=User)
def create_requisitioner(sender, instance, created, **kwargs):
    if created:
        department = Department.objects.get(code='SEAS')
        Requisitioner.objects.create(user=instance,department=department)

@receiver(post_save, sender=User)
def save_requisitioner(sender, instance, **kwargs):
    instance.requisitioner.save() 

@receiver(post_save, sender=Tracker)
def post_save_tracker_update(sender, instance, created, **kwargs):
    # tracker = Tracker.objects.get(id=instance.id)
    response = update_tracking_details(instance.tracking_number, instance.carrier.carrier_code)

    # Update values on Tracker
    if instance.status != response.get('status'):
        instance.status = response.get('status')
        instance.delivery_estimate = response.get('delivery_estimate')
        instance.events = response.get('events')
        instance.save()

    _, _ = create_events(instance,instance.events)


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
    data = [{
        'Status': "Submitted",
        'First Name': instance.requisitioner.user.first_name,
        'Last Name': instance.requisitioner.user.last_name,
        'Requestor': instance.requisitioner.user.email,
        'Requestor WSU ID#': 'sometext1'
    }]