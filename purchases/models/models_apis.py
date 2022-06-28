from django.conf import settings
from django.db import models
import json, http.client


from .models_metadata import Carrier

class Tracker(models.Model):
    id = models.CharField(max_length=100, primary_key=True, editable=False,null=False)
    carrier = models.ForeignKey(Carrier,on_delete=models.PROTECT,blank=True,null=True)
    tracking_number = models.CharField(max_length=100)
    events = models.JSONField(default=None,blank=True,null=True)
    shipment_id = models.CharField(max_length=100,blank=True,null=True)
    status = models.CharField(max_length=50,blank=True,null=True)
    delivery_estimate = models.DateTimeField(blank=True,null=True)

    class Meta:
        indexes = [
            models.Index(fields=['id'])
        ]

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