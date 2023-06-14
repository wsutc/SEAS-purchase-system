import json
from datetime import datetime, timedelta
from http import HTTPStatus
from json import JSONDecodeError
from random import choice

import pytz
from django.contrib.auth.models import Permission, User

# from django.core.management import call_command
from django.db import models
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from model_bakery import baker
from model_bakery.recipe import seq

from purchases.models.models_base import TrackingWebhookMessage
from purchases.tracking import get_generated_signature
from purchases.views import tracking_webhook

# from .management.commands import create_sample_data  # noqa: F401
from .models import PurchaseRequest, Requisitioner, Tracker, Urgency

# from .timer import Timer


def create_pr_deps():
    user = baker.make(User, first_name=seq("Test"), last_name=seq("User"))
    # from purchases.signals import create_requisitioner
    requisitioner = Requisitioner.objects.get(user=user)
    # requisitioner.save()
    # requisitioner = baker.make(Requisitioner)
    # user = requisitioner.user
    print(f"Requisitioner First Name: {requisitioner.user.first_name}")
    print(f"Requisitioner Last Name: {requisitioner.user.last_name}")
    # create_requisitioner(sender=User, instance=user, created=True)
    rvalue = {
        "default_sales_tax_rate": baker.make_recipe(
            "purchases.sales_tax_rate_settings"
        ),
        "vendor": baker.make_recipe("purchases.vendor_tormach"),
        "urgency": baker.make(Urgency, name="Standard"),
        "user": user,
        "requisitioner": Requisitioner.objects.get(user=user),
    }

    return rvalue


def get_random_object(model: models):
    pk_list = model.objects.values_list("pk", flat=True)
    random_pk = choice(pk_list)

    return model.objects.get(pk=random_pk)


class PurchaseRequestTestModel(TestCase):
    def setUp(self):
        deps = create_pr_deps()
        self.purchase_request = baker.make(
            PurchaseRequest,
            requisitioner=deps["requisitioner"],
            vendor=deps["vendor"],
            sales_tax_rate=deps["default_sales_tax_rate"].value,
            urgency=deps["urgency"],
        )

    def test_using_purchase_request(self):
        self.assertIsInstance(self.purchase_request, PurchaseRequest)
        self.assertNotEqual(self.purchase_request.slug, "")
        self.assertNotEqual(self.purchase_request.requisitioner.slug, "")


class TestCreatePRView(TestCase):
    def setUp(self):
        deps = create_pr_deps()
        self.user = deps["user"]
        self.purchase_request = baker.make(
            PurchaseRequest,
            requisitioner=deps["requisitioner"],
            vendor=deps["vendor"],
            sales_tax_rate=deps["default_sales_tax_rate"].value,
            urgency=deps["urgency"],
        )

    def test_anonymous_cannot_see_page(self):
        response = self.client.get(reverse("new_pr"))
        self.assertRedirects(
            response, "/accounts/login/?next=/purchases/purchase-request/new/"
        )

    def test_permissed_user_can_see_page(self):
        self.user.user_permissions.add(
            Permission.objects.get(codename="add_purchaserequest")
        )

        self.client.force_login(user=self.user)
        response = self.client.get(reverse("new_pr"))
        print(f"response.status_code: {response.status_code}")
        self.assertEqual(response.status_code, 200)


# class ListViewTiming(TestCase):
#     def setUp(self):
#         call_command("create_sample_data")
#         self.user = get_random_object(User)
#         print(f"Random User: {self.user.username}")

#     def test_pr_list_full(self):
#         self.client.force_login(user=self.user)
#         c = Client()

#         t = Timer()
#         t.start()
#         response = c.get(reverse("home"))
#         t.stop()

#         self.assertEqual(response.status_code, 200)


@override_settings(PYTRACK_17TRACK_KEY="abc123")
class TrackingWebhookTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.purchase_request = baker.prepare_recipe("purchases.default_pr")
        self.tracker = baker.prepare(Tracker)
        # TODO - find a way to get the message instead of hard coding it
        self.valid_signature = get_generated_signature(
            b"--BoUnDaRyStRiNg--\r\n", "abc123"
        )

    def test_bad_method(self):
        url = reverse(tracking_webhook)
        print(f"Webhook URL: {url}")
        response = self.client.get(url)
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    def test_missing_token(self):
        response = self.client.post(reverse(tracking_webhook))

        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_bad_token(self):
        response = self.client.post(
            reverse(tracking_webhook), headers={"sign": "def456"}
        )

        assert response.status_code == HTTPStatus.FORBIDDEN
        assert response.content.decode() == "Inconsistency in response signature."

    def test_valid_token(self):
        # since there is no body, post will fail, but with known exception
        self.assertRaises(
            JSONDecodeError,
            self.client.post,
            path=reverse(tracking_webhook),
            HTTP_SIGN=self.valid_signature,
        )

    def test_success(self):
        start = datetime.today()
        start_aware = pytz.utc.localize(start)
        received = start - timedelta(days=100)
        old_message = TrackingWebhookMessage.objects.create(
            received_at=pytz.utc.localize(received)
        )

        message = json.dumps(WEBHOOK_DATA).encode("utf-8")
        sign = get_generated_signature(message, "abc123")

        response = self.client.post(
            reverse(tracking_webhook),
            headers={"sign": sign},
            content_type="application/json",
            data=WEBHOOK_DATA,
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.content.decode(), "Message successfully received.")

        # assert response.status_code == HTTPStatus.OK
        # assert response.content.decode() == "Message successfully received."
        self.assertFalse(
            TrackingWebhookMessage.objects.filter(id=old_message.id).exists()
        )

        awm = TrackingWebhookMessage.objects.get()

        self.assertGreaterEqual(awm.received_at, start_aware)
        # self.assertDictEqual(awm.payload, {"this": "is a message"})
        # assert awm.received_at >= start
        # assert awm.payload == {"this": "is a message"}


#     def test_tracker_update(self):
#         pass

null = "null"


WEBHOOK_DATA = {
    "event": "TRACKING_UPDATED",
    "data": {
        "number": "1Z2617V10397725789",
        "carrier": 3011,
        "param": null,
        "tag": null,
        "track_info": {
            "shipping_info": {
                "shipper_address": {
                    "country": "US",
                    "state": "CA",
                    "city": "CITY OF INDUSTRY",
                    "street": null,
                    "postal_code": null,
                    "coordinates": {"longitude": null, "latitude": null},
                }
            },
            "recipient_address": {
                "country": "US",
                "state": "CA",
                "city": "GASQUET",
                "street": null,
                "postal_code": null,
                "coordinates": {"longitude": null, "latitude": null},
            },
        },
        "latest_status": {
            "status": "Delivered",
            "sub_status": "Delivered_Other",
            "sub_status_descr": null,
        },
        "latest_event": {
            "time_iso": "2022-04-04T16:35:22-07:00",
            "time_utc": "2022-04-04T23:35:22Z",
            "description": "DELIVERED",
            "location": "GASQUET, CA, US",
            "stage": null,
            "address": {
                "country": "US",
                "state": "CA",
                "city": "GASQUET",
                "street": null,
                "postal_code": null,
                "coordinates": {"longitude": null, "latitude": null},
            },
        },
        "time_metrics": {
            "days_after_order": 7,
            "days_of_transit": 4,
            "days_of_transit_done": 4,
            "days_after_last_update": 0,
            "estimated_delivery_date": {
                "source": null,
                "from": null,
                "to": null,
            },
        },
        "milestone": [
            {
                "key_stage": "InfoReceived",
                "time_iso": "2022-03-28T22:43:08-07:00",
                "time_utc": "2022-03-29T05:43:08Z",
            },
            {"key_stage": "PickedUp", "time_iso": null, "time_utc": null},
            {"key_stage": "Departure", "time_iso": null, "time_utc": null},
            {"key_stage": "Arrival", "time_iso": null, "time_utc": null},
            {
                "key_stage": "AvailableForPickup",
                "time_iso": null,
                "time_utc": null,
            },
            {
                "key_stage": "OutForDelivery",
                "time_iso": "2022-04-04T08:46:06-07:00",
                "time_utc": "2022-04-04T15:46:06Z",
            },
            {
                "key_stage": "Delivered",
                "time_iso": "2022-04-04T16:35:22-07:00",
                "time_utc": "2022-04-04T23:35:22Z",
            },
            {"key_stage": "Returning", "time_iso": null, "time_utc": null},
            {"key_stage": "Returned", "time_iso": null, "time_utc": null},
        ],
        "misc_info": {
            "risk_factor": 0,
            "service_type": "UPS Ground",
            "weight_raw": "49.20LBS",
            "weight_kg": "22.32",
            "pieces": null,
            "dimensions": null,
            "customer_number": "2617V1",
            "reference_number": null,
            "local_number": "",
            "local_provider": "",
            "local_key": 0,
        },
        "tracking": {
            "providers_hash": -595601716,
            "providers": [
                {
                    "provider": {
                        "key": 100002,
                        "name": "UPS",
                        "alias": "UPS",
                        "tel": null,
                        "homepage": "http://www.ups.com/",
                        "country": "",
                    },
                    "service_type": "UPS Ground",
                    "latest_sync_status": "Success",
                    "latest_sync_time": "2022-04-29T08:06:06Z",
                    "events_hash": -925320483,
                    "events": [
                        {
                            "time_iso": "2022-04-04T16:35:22-07:00",
                            "time_utc": "2022-04-04T23:35:22Z",
                            "description": "DELIVERED",
                            "location": "GASQUET, CA, US",
                            "stage": "Delivered",
                            "address": {
                                "country": "US",
                                "state": "CA",
                                "city": "GASQUET",
                                "street": null,
                                "postal_code": null,
                                "coordinates": {
                                    "longitude": null,
                                    "latitude": null,
                                },
                            },
                        },
                        {
                            "time_iso": "2022-04-04T08:46:06-07:00",
                            "time_utc": "2022-04-04T15:46:06Z",
                            "description": "Out For Delivery Today",
                            "location": "Crescent City, CA, US",
                            "stage": "OutForDelivery",
                            "address": {
                                "country": "US",
                                "state": "CA",
                                "city": "Crescent City",
                                "street": null,
                                "postal_code": null,
                                "coordinates": {
                                    "longitude": null,
                                    "latitude": null,
                                },
                            },
                        },
                        {
                            "time_iso": "2022-04-02T02:15:00-07:00",
                            "time_utc": "2022-04-02T09:15:00Z",
                            "description": "Arrived at Facility",
                            "location": "Anderson, CA, US",
                            "stage": null,
                            "address": {
                                "country": "US",
                                "state": "CA",
                                "city": "Anderson",
                                "street": null,
                                "postal_code": null,
                                "coordinates": {
                                    "longitude": null,
                                    "latitude": null,
                                },
                            },
                        },
                        {
                            "time_iso": "2022-03-31T16:36:47-07:00",
                            "time_utc": "2022-03-31T23:36:47Z",
                            "description": "Origin Scan",
                            "location": "Ontario, CA, US",
                            "stage": null,
                            "address": {
                                "country": "US",
                                "state": "CA",
                                "city": "Ontario",
                                "street": null,
                                "postal_code": null,
                                "coordinates": {
                                    "longitude": null,
                                    "latitude": null,
                                },
                            },
                        },
                        {
                            "time_iso": "2022-03-28T22:43:08-07:00",
                            "time_utc": "2022-03-29T05:43:08Z",
                            "description": "Shipper created a label, UPS has not received the package yet.",  # noqa: E501
                            "location": "US",
                            "stage": "InfoReceived",
                            "address": {
                                "country": "US",
                                "state": null,
                                "city": null,
                                "street": null,
                                "postal_code": null,
                                "coordinates": {
                                    "longitude": null,
                                    "latitude": null,
                                },
                            },
                        },
                    ],
                }
            ],
        },
    },
}
