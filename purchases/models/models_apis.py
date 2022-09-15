from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from purchases.models.models_data import PurchaseRequest, SimpleProduct
from purchases.tracking import TrackerObject

from .models_metadata import Carrier

from django_listview_filters._helpers import get_setting

from django.utils.translation import gettext_lazy as _

from furl import furl

import logging

logger = logging.getLogger(__name__)


class Tracker(models.Model):
    id = models.CharField(max_length=100, primary_key=True, editable=False, null=False)
    active = models.BooleanField(default=True)
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
    received = models.BooleanField(_("package received"), default=False)
    simple_product = models.ManyToManyField(
        SimpleProduct, verbose_name=_("items"), through="TrackerItem"
    )

    @property
    def latest_event(self):
        latest_event = self.trackingevent_set.latest()
        return latest_event

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
        tracking_patterns = get_setting("TRACKER_PARAMS", ["trackingnumber"])

        for pattern in tracking_patterns:
            logger.info("{}".format(pattern))

        try:
            path = furl(self.carrier.tracking_link)

            tracking_param = [
                param for param in path.args if param.lower() in tracking_patterns
            ]

            if len(tracking_param) == 1:
                path.args[tracking_param[0]] = self.tracking_number
            else:
                raise KeyError(path)

            return path.url
        except:
            return None

    def update_tracker_fields(self, tracker_obj: TrackerObject) -> bool:
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
            delivery_estimate = tracker_obj.delivery_estimate
        else:
            delivery_estimate = None

        if self.delivery_estimate != delivery_estimate:
            update_fields["delivery_estimate"] = delivery_estimate

        if tracker_obj.carrier_code:
            carrier, _ = Carrier.objects.get_or_create(
                carrier_code=tracker_obj.carrier_code,
                defaults={"name": tracker_obj.carrier_name},
            )
            update_fields["carrier"] = carrier

        if len(update_fields):
            count = qs.update(**update_fields)
            return True if count > 0 else False
        else:
            return False

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

    def stop(self):
        tracker = self.__class__.objects.filter(pk=self.pk)

        return True if tracker.update(active=False) else False


class TrackerItem(models.Model):
    tracker = models.ForeignKey(
        Tracker, verbose_name=_("tracker"), on_delete=models.CASCADE
    )
    simple_product = models.ForeignKey(
        SimpleProduct, verbose_name=_("item"), on_delete=models.CASCADE
    )
    quantity = models.DecimalField(
        _("quantity in shipment"), max_digits=15, decimal_places=3
    )
    missing = models.BooleanField(_("missing"), default=False)

    @property
    def shipment_received(self):
        return self.tracker.received

    def __str__(self) -> str:
        value = "{item} | {tracker}".format(
            item=self.simple_product, tracker=self.tracker
        )
        return value


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


class TrackerStatusSteps(models.Model):
    tracker_status = models.CharField(_("status"), max_length=50)
    rank = models.PositiveSmallIntegerField(
        _("rank"), help_text=_("rank in sort order"), unique=True
    )
