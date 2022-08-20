from datetime import datetime
from time import strptime
from django.db import models
from django.db.models import Min
from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse
from django.utils.text import slugify

from purchases.models.models_data import PurchaseRequest
# from purchases.tracking import register_tracker


from .models_metadata import Carrier

class TrackerManager(models.Manager):
    def get_queryset(self):
        # first_event_time=Min('trackingevent__time_utc')
        qs = super().get_queryset().annotate(time_utc=Min('trackingevent__time_utc')).order_by('-time_utc')
        # does_exist = qs.exists()
        return qs

class Tracker(models.Model):
    id = models.CharField(max_length=100, primary_key=True, editable=False,null=False)
    carrier = models.ForeignKey(Carrier,on_delete=models.PROTECT,blank=True,null=True)
    tracking_number = models.CharField(max_length=100)
    events = models.JSONField(default=None,blank=True,null=True)
    events_hash = models.CharField(max_length=100, editable=False,null=True)
    shipment_id = models.CharField(max_length=100,blank=True,null=True)
    status = models.CharField(max_length=50,blank=True,null=True)
    sub_status = models.CharField(max_length=50,editable=False,null=True)
    delivery_estimate = models.DateTimeField(blank=True,null=True)
    purchase_request = models.ForeignKey(PurchaseRequest,on_delete=models.CASCADE,null=True)

    objects_ordered = TrackerManager()
    objects = models.Manager()

    class Meta:
        indexes = [
            models.Index(fields=['id'])
        ]
        constraints = [
            models.UniqueConstraint(fields = ('tracking_number','carrier'),name='unique_tracking_number_carrier')
        ]
        # ordering = ['-trackingevent_set__time_utc_first']

    def get_absolute_url(self):
        kwargs = {
            'pk': slugify(self.id, allow_unicode=True)
        }
        return reverse('tracker_detail', kwargs=kwargs)

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.id = self.tracking_number
        super().save(*args, **kwargs)

    def get_tracking_link(self):
        try:
            return "%s%s" % (self.carrier.tracking_link, self.tracking_number)
        except:
            return None
        # if stub := self.carrier.tracking_link:
        #     return "%s%s" % (stub,self.tracking_number)
        # else:
        #     return None

    def __str__(self):
        value = "{0} {1}".format(self.carrier,self.tracking_number)
        return str(value)

class TrackingWebhookMessage(models.Model):
    received_at = models.DateTimeField(help_text="DateTime that message was recieved.")
    payload = models.JSONField(default=None, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['received_at'])
        ]

class TrackingEvent(models.Model):
    tracker = models.ForeignKey(Tracker,on_delete=models.CASCADE)
    time_utc = models.DateTimeField()
    description = models.TextField(null=True)
    location = models.CharField(max_length=100, blank=True)
    stage = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ['-time_utc']
        get_latest_by = ['time_utc']

    def __str__(self):
        value = "{location}; {description}; {time}".format(location=self.location,description=self.description,time=self.time_utc.strftime("%c %Z"))
        return value

def create_events(tracker:Tracker, events) -> tuple[list[TrackingEvent], list[TrackingEvent]]:
    created_events = []
    updated_events = []
    for event in events:
        event_object, created = TrackingEvent.objects.update_or_create(
            tracker = tracker,
            time_utc = event['time_utc'],
            location = event['location'],
            defaults= {
                'description': event['description'],
                'stage': event['stage']
            }
        )

        if created:
            created_events.append(event_object)
        else:
            updated_events.append(event_object)

    return (created_events,updated_events)

def update_tracker_fields(tracker:Tracker,fields:dict) -> int:
    """Updates <tracker> using <fields>"""
    qs = Tracker.objects.filter(pk=tracker.pk)          # using `queryset.update` prevents using `model.save`, therefore, no `post_save` signal

    update_fields = {}                                  # create a dict of fields with values to send to the ``.update` method
    if tracker.status != (status := fields.get('status')):
        update_fields['status'] = status

    if tracker.sub_status != (sub_status := fields.get('sub_status')):
        update_fields['sub_status'] = sub_status

    if delivery_estimate := fields.get('delivery_estimate'):
        delivery_estimate = datetime.fromisoformat(delivery_estimate)
    else:
        delivery_estimate = None

    if tracker.delivery_estimate != delivery_estimate:
        update_fields['delivery_estimate'] = delivery_estimate

    events_hash = str(fields.get('events_hash'))

    if tracker.events_hash != events_hash:
        _, _ = create_events(tracker,fields.get('events'))

        update_fields['events'] = fields.get('events')      # This is the JSON field, *not* the TrackingEvent model
        update_fields['events_hash'] = events_hash

    if 'carrier' in fields:
        update_fields['carrier'] = fields.get('carrier')

    if len(update_fields):
        count = qs.update(**update_fields)
        # qs.update(status=status)
        return count
    else:
        return None