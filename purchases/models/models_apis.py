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

    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)

    # def update(self):
    #     api_key = settings.SHIP24_KEY
    #     # id = self.id
    #     tracking_number = self.tracking_number
    #     conn = http.client.HTTPSConnection("api.ship24.com")
    #     headers = {
    #         'Content-Type': "application/json",
    #         'Authorization': "Bearer " + api_key
    #     }

    #     get_path = "/public/v1/trackers/search/%s" % (tracking_number)

    #     conn.request("GET", get_path, headers=headers)
    #     response = conn.getresponse()
    #     data = response.read()
    #     dataJson = json.loads(data.decode("utf-8"))
    #     # print(dataJson)
    #     dataDict = dataJson.get('data')
    #     trackings = dataDict.get('trackings')
    #     # tracker = trackings[0].get('tracker')
    #     shipment = trackings[0].get('shipment')
    #     events = trackings[0].get('events')
    #     event_data = get_event_data(events[0])

    #     if courier_code := event_data.get('courier_code'):                              # Only attempt if courier_code is present
    #         carrier, _ = Carrier.objects.get_or_create(                                 # Create new courier if match not found
    #             slug = courier_code,
    #             defaults = {'name': courier_code}
    #         )
    #         self.carrier = carrier

    #     self.shipment_id = shipment.get('shipmentId')
        
    #     self.delivery_estimate = shipment.get('delivery').get('estimatedDeliveryDate')
    #     self.events = events
    #     if status := shipment.get('statusCode'):
    #         self.status = status
    #     elif status := event_data.get('event_status'):
    #         self.status = status
    #     self.save()

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