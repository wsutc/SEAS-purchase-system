from datetime import datetime
from time import strptime
from django.db import models
from django.db.models import Min
from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse
from django.utils.text import slugify

from purchases.models.models_data import PurchaseRequest
from purchases.tracking import TrackerObject

# from purchases.tracking import register_tracker


from .models_metadata import Carrier


class TrackerManager(models.Manager):
    def get_queryset(self):
        # first_event_time=Min('trackingevent__time_utc')
        qs = (
            super()
            .get_queryset()
            .annotate(time_utc=Min("trackingevent__time_utc"))
            .order_by("-time_utc")
        )
        # qs = super().get_queryset().order_by('-first_event_time')
        # does_exist = qs.exists()
        return qs


class Tracker(models.Model):
    id = models.CharField(max_length=100, primary_key=True, editable=False, null=False)
    carrier = models.ForeignKey(
        Carrier, on_delete=models.PROTECT, blank=True, null=True
    )
    tracking_number = models.CharField(max_length=100)
    events = models.JSONField(default=None, blank=True, null=True)
    events_hash = models.CharField(max_length=100, editable=False, null=True)
    shipment_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)
    sub_status = models.CharField(max_length=50, editable=False, null=True)
    delivery_estimate = models.DateTimeField(blank=True, null=True)
    purchase_request = models.ForeignKey(
        PurchaseRequest, on_delete=models.CASCADE, null=True
    )
    earliest_event_time = models.DateTimeField(blank=True, null=True, editable=False)

    # objects_ordered = TrackerManager()
    # objects = models.Manager()

    class Meta:
        indexes = [models.Index(fields=["id"])]
        constraints = [
            models.UniqueConstraint(
                fields=("tracking_number", "carrier"),
                name="unique_tracking_number_carrier",
            )
        ]
        ordering = ["-earliest_event_time"]

    def get_absolute_url(self):
        kwargs = {"pk": slugify(self.id, allow_unicode=True)}
        return reverse("tracker_detail", kwargs=kwargs)

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

    def update_tracker_fields(self, tracker_obj: TrackerObject) -> int:
        """Updates <tracker> using <fields>"""
        qs = Tracker.objects.filter(
            pk=self.pk
        )  # using `queryset.update` prevents using `model.save`, therefore, no `post_save` signal

        update_fields = (
            {}
        )  # create a dict of fields with values to send to the ``.update` method
        if self.status != tracker_obj.status:
            update_fields["status"] = tracker_obj.status

        if self.sub_status != tracker_obj.sub_status:
            update_fields["sub_status"] = tracker_obj.sub_status

        if delivery_estimate := tracker_obj.delivery_estimate:
            # delivery_estimate = datetime.fromisoformat(delivery_estimate)
            delivery_estimate = tracker_obj.delivery_estimate
        else:
            delivery_estimate = None

        if self.delivery_estimate != delivery_estimate:
            update_fields["delivery_estimate"] = delivery_estimate

        # events_hash = str(fields.get('events_hash'))

        # if tracker.events_hash != events_hash:
        #     _, _ = create_events(tracker,fields.get('events'))

        #     update_fields['events'] = fields.get('events')      # This is the JSON field, *not* the TrackingEvent model
        #     update_fields['events_hash'] = events_hash

        if tracker_obj.carrier_code:
            carrier, _ = Carrier.objects.get_or_create(
                carrier_code=tracker_obj.carrier_code,
                defaults={"name": tracker_obj.carrier_name},
            )
            update_fields["carrier"] = carrier

        if len(update_fields):
            count = qs.update(**update_fields)
            # qs.update(status=status)
            return count
        else:
            return None

    def create_events(self, events) -> tuple[list, list]:
        created_events = []
        updated_events = []
        set_first_time = False
        if not self.earliest_event_time:
            set_first_time = True

        for event in events:
            event_object, created = TrackingEvent.objects.update_or_create(
                tracker=self,
                time_utc=event["time_utc"],
                location=event["location"],
                defaults={"description": event["description"], "stage": event["stage"]},
            )

            if created:
                created_events.append(event_object)
            else:
                updated_events.append(event_object)

        if set_first_time:
            self.earliest_event_time = self.trackingevent_set.earliest().time_utc

        return (created_events, updated_events)

    def __str__(self):
        value = "{0} {1}".format(self.carrier, self.tracking_number)
        return str(value)


class TrackingWebhookMessage(models.Model):
    received_at = models.DateTimeField(help_text="DateTime that message was recieved.")
    payload = models.JSONField(default=None, null=True)

    class Meta:
        indexes = [models.Index(fields=["received_at"])]


class TrackingEvent(models.Model):
    tracker = models.ForeignKey(Tracker, on_delete=models.CASCADE)
    time_utc = models.DateTimeField()
    description = models.TextField(null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    stage = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        ordering = ["-time_utc"]
        get_latest_by = ["time_utc"]

    def __str__(self):
        value = "{location}; {description}; {time}".format(
            location=self.location,
            description=self.description,
            time=self.time_utc.strftime("%c %Z"),
        )
        return value
