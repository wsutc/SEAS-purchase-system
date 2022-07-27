from django.conf import settings
from django.db import models
import json, http.client

from purchases.models.models_data import PurchaseRequest
from purchases.tracking import get_tracker, register_tracker


from .models_metadata import Carrier

class Tracker(models.Model):
    id = models.CharField(max_length=100, primary_key=True, editable=False,null=False)
    carrier = models.ForeignKey(Carrier,on_delete=models.PROTECT,blank=True,null=True)
    tracking_number = models.CharField(max_length=100)
    events = models.JSONField(default=None,blank=True,null=True)
    shipment_id = models.CharField(max_length=100,blank=True,null=True)
    status = models.CharField(max_length=50,blank=True,null=True)
    delivery_estimate = models.DateTimeField(blank=True,null=True)
    purchase_request = models.ForeignKey(PurchaseRequest,on_delete=models.CASCADE,null=True)

    class Meta:
        indexes = [
            models.Index(fields=['id'])
        ]
        constraints = [
            models.UniqueConstraint(fields = ('tracking_number','carrier'),name='unique_tracking_number_carrier')
        ]

    def save(self, *args, **kwargs):
        if self._state.adding:
            
            # if self.carrier:
            if not Tracker.objects.filter(tracking_number = self.tracking_number, carrier = self.carrier).exists():

                n,c,m,r = register_tracker(self.tracking_number, self.carrier.carrier_code)

                if r:
                    self.carrier, _ = Carrier.objects.get_or_create(
                        carrier_code = c,
                        defaults={
                            'name': c
                        }
                    )
                    self.tracking_number = n
                    self.id = n
                else:
                    raise KeyError('No valid trackers created. Is the tracker already registered?')

                
            else:
                raise

        super().save(*args, **kwargs)

    def get_tracking_link(self):
        if stub := self.carrier.tracking_link:
            return "%s%s" % (stub,self.tracking_number)
        else:
            return None

    def __str__(self):
        return str(self.id)

def get_event_data(event):
    event_data = {
        'event_id': event.get('eventId'),
        'event_status': event.get('status'),
        'event_datetime': event.get('datetime'),
        'courier_code': event.get('courierCode')
    }

    return event_data

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
    description = models.TextField(max_length=150,null=True)
    location = models.CharField(max_length=100,null=True)
    stage = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        ordering = ['-time_utc']
        get_latest_by = ['time_utc']

    def __str__(self):
        return "%s; %s; %s" % (self.location,self.description,self.time_utc.strftime("%c %Z"))

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