from http import HTTPStatus

from django.contrib.auth.models import Permission, User
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from model_bakery import baker

from purchases.views import tracking_webhook

from .models import PurchaseRequest, Requisitioner, Tracker, Urgency


def create_pr_deps():
    user = baker.make(User)
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
        self.assertEqual(response.status_code, 200)


@override_settings(PYTRACK_17TRACK_KEY="abc123")
class TrackingWebhookTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.purchase_request = baker.prepare_recipe("purchases.default_pr")
        self.tracker = baker.prepare(Tracker)

    def test_bad_method(self):
        url = reverse(tracking_webhook)
        response = self.client.get(url)
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    def test_missing_token(self):
        response = self.client.post(reverse(tracking_webhook))

        assert response.status_code == HTTPStatus.FORBIDDEN


#     def test_bad_token(self):
#         response = self.client.post(
#             reverse(tracking_webhook),
#             HTTP_AFTERSHIP_WEBHOOK_SECRET = "def456"
#         )

#         assert response.status_code == HTTPStatus.FORBIDDEN
#         assert (
#             response.content.decode() == "Incorrect token in Aftership-Hmac-Sha256 header."  # noqa: E501
#         )

#     def test_success(self):

#         start = timezone.now()
#         old_message = TrackingWebhookMessage.objects.create(
#             received_at = start - dt.timedelta(days=100)
#         )

#         response = self.client.post(
#             reverse(tracking_webhook),
#             HTTP_AFTERSHIP_HMAC_SHA256="abc123",
#             content_type="application/json",
#             data={
#                 "event_id": "bca2a741-8613-4694-bfb4-2ceb0016ee4f",
#                 "event": "tracking_update",
#                 "is_tracking_first_tag": "true",
#                 "msg": {
#                     "id": "n33xyn2b61cm3kosdtnvu00e",
#                     "tracking_number": "9405516902697649303570",
#                     "title": "9405516902697649303570",
#                     "note": "null",
#                     "origin_country_iso3": "USA",
#                     "destination_country_iso3": "USA",
#                     "courier_destination_country_iso3": "USA",
#                     "shipment_package_count": "null",
#                     "active": "true",
#                     "order_id": "null",
#                     "order_id_path": "null",
#                     "order_date": "null",
#                     "customer_name": "null",
#                     "source": "web",
#                     "emails": [
#                         "hx.zuo@aftership.com"
#                     ],
#                     "smses": [],
#                     "subscribed_smses": [],
#                     "subscribed_emails": [],
#                     "android": [],
#                     "ios": [],
#                     "return_to_sender": "false",
#                     "custom_fields": {},
#                     "tag": "InTransit",
#                     "subtag": "InTransit_003",
#                     "subtag_message": "Arrival scan",
#                     "tracked_count": 1,
#                     "expected_delivery": "2021-05-17",
#                     "signed_by": "null",
#                     "shipment_type": "Priority Mail",
#                     "created_at": "2021-05-17T09:05:29+00:00",
#                     "updated_at": "2021-05-17T09:05:31+00:00",
#                     "slug": "usps",
#                     "unique_token": "deprecated",
#                     "path": "deprecated",
#                     "shipment_weight": "null",
#                     "shipment_weight_unit": "null",
#                     "delivery_time": 5,
#                     "last_mile_tracking_supported": "true",
#                     "language": "null",
#                     "shipment_pickup_date": "2021-05-13T18:10:00",
#                     "shipment_delivery_date": "null",
#                     "last_updated_at": "2021-05-17T09:05:31+00:00",
#                     "checkpoints": [
#                         {
#                             "location": "BOCA RATON, FL, 33487, USA, United States",
#                             "country_name": "United States",
#                             "country_iso3": "USA",
#                             "state": "FL",
#                             "city": "BOCA RATON",
#                             "zip": "33487",
#                             "message": "Shipping Label Created, USPS Awaiting Item",
#                             "coordinates": [],
#                             "tag": "InfoReceived",
#                             "subtag": "InfoReceived_001",
#                             "subtag_message": "Info Received",
#                             "created_at": "2021-05-17T09:05:31+00:00",
#                             "checkpoint_time": "2021-05-13T13:04:00",
#                             "slug": "usps",
#                             "raw_tag": "GX"
#                         },
#                         {
#                             "location": "BOCA RATON, FL, 33487, USA, United States",
#                             "country_name": "United States",
#                             "country_iso3": "USA",
#                             "state": "FL",
#                             "city": "BOCA RATON",
#                             "zip": "33487",
#                             "message": "Accepted at USPS Origin Facility",
#                             "coordinates": [],
#                             "tag": "InTransit",
#                             "subtag": "InTransit_002",
#                             "subtag_message": "Acceptance scan",
#                             "created_at": "2021-05-17T09:05:31+00:00",
#                             "checkpoint_time": "2021-05-13T18:10:00",
#                             "slug": "usps",
#                             "raw_tag": "OA"
#                         },
#                         {
#                             "location": "WEST PALM BEACH FL DISTRIBUTION CENTER",
#                             "country_name": "United States",
#                             "country_iso3": "USA",
#                             "state": "null",
#                             "city": "WEST PALM BEACH FL DISTRIBUTION CENTER",
#                             "zip": "null",
#                             "message": "Arrived at USPS Regional Origin Facility",
#                             "coordinates": [],
#                             "tag": "InTransit",
#                             "subtag": "InTransit_003",
#                             "subtag_message": "Arrival scan",
#                             "created_at": "2021-05-17T09:05:31+00:00",
#                             "checkpoint_time": "2021-05-13T19:25:00",
#                             "slug": "usps",
#                             "raw_tag": "10"
#                         },
#                         {
#                             "location": "WEST PALM BEACH FL DISTRIBUTION CENTER",
#                             "country_name": "United States",
#                             "country_iso3": "USA",
#                             "state": "null",
#                             "city": "WEST PALM BEACH FL DISTRIBUTION CENTER",
#                             "zip": "null",
#                             "message": "Departed USPS Regional Origin Facility",
#                             "coordinates": [],
#                             "tag": "InTransit",
#                             "subtag": "InTransit_007",
#                             "subtag_message": "Departure Scan",
#                             "created_at": "2021-05-17T09:05:31+00:00",
#                             "checkpoint_time": "2021-05-14T00:25:00",
#                             "slug": "usps",
#                             "raw_tag": "10"
#                         },
#                         {
#                             "location": "FAYETTEVILLE NC DISTRIBUTION CENTER ANNEX",
#                             "country_name": "United States",
#                             "country_iso3": "USA",
#                             "state": "null",
#                             "city": "FAYETTEVILLE NC DISTRIBUTION CENTER ANNEX",
#                             "zip": "null",
#                             "message": "Arrived at USPS Regional Destination Facility",  # noqa: E501
#                             "coordinates": [],
#                             "tag": "InTransit",
#                             "subtag": "InTransit_003",
#                             "subtag_message": "Arrival scan",
#                             "created_at": "2021-05-17T09:05:31+00:00",
#                             "checkpoint_time": "2021-05-15T13:06:00",
#                             "slug": "usps",
#                             "raw_tag": "10"
#                         },
#                         {
#                             "location": "FAYETTEVILLE NC DISTRIBUTION CENTER ANNEX",
#                             "country_name": "United States",
#                             "country_iso3": "USA",
#                             "state": "null",
#                             "city": "FAYETTEVILLE NC DISTRIBUTION CENTER ANNEX",
#                             "zip": "null",
#                             "message": "Departed USPS Regional Facility",
#                             "coordinates": [],
#                             "tag": "InTransit",
#                             "subtag": "InTransit_007",
#                             "subtag_message": "Departure Scan",
#                             "created_at": "2021-05-17T09:05:31+00:00",
#                             "checkpoint_time": "2021-05-16T05:52:00",
#                             "slug": "usps",
#                             "raw_tag": "T1"
#                         },
#                         {
#                             "location": "HOLLY RIDGE, NC, 28445, USA, United States",
#                             "country_name": "United States",
#                             "country_iso3": "USA",
#                             "state": "NC",
#                             "city": "HOLLY RIDGE",
#                             "zip": "28445",
#                             "message": "Arrived at Post Office",
#                             "coordinates": [],
#                             "tag": "InTransit",
#                             "subtag": "InTransit_003",
#                             "subtag_message": "Arrival scan",
#                             "created_at": "2021-05-17T09:05:31+00:00",
#                             "checkpoint_time": "2021-05-17T03:45:00",
#                             "slug": "usps",
#                             "raw_tag": "07"
#                         }
#                     ],
#                     "order_promised_delivery_date": "null",
#                     "delivery_type": "null",
#                     "pickup_location": "null",
#                     "pickup_note": "null",
#                     "tracking_account_number": "null",
#                     "tracking_origin_country": "null",
#                     "tracking_destination_country": "null",
#                     "tracking_key": "null",
#                     "tracking_postal_code": "null",
#                     "tracking_ship_date": "null",
#                     "tracking_state": "null",
#                     "courier_tracking_link": "https://tools.usps.com/go/TrackConfirmAction?tLabels=9405516902697649303570",  # noqa: E501
#                     "first_attempted_at": "null",
#                     "courier_redirect_link": "https://tools.usps.com/go/TrackConfirmAction?tRef=fullpage&tLc=2&text28777=&tLabels=9405516902697649303570%2C",  # noqa: E501
#                     "on_time_status": "trending-on-time",
#                     "on_time_difference": 0,
#                     "order_tags": [],
#                     "aftership_estimated_delivery_date": {
#                                 "estimated_delivery_date": "2022-01-03",
#                                 "confidence_score": "null",
#                                 "estimated_delivery_date_min": "2022-01-01",
#                                 "estimated_delivery_date_max": "2022-01-06"
#                     }
#                     },
#                     "ts": 1621242332
#                     }
#                 )

#         assert response.status_code == HTTPStatus.OK
#         assert response.content.decode() == "Message successfully received."
#         assert not TrackingWebhookMessage.objects.filter(id=old_message.id).exists()
#         awm = TrackingWebhookMessage.objects.get()
#         assert awm.received_at >= start
#         # assert awm.payload == {"this": "is a message"}

#     def test_tracker_update(self):
#         pass
