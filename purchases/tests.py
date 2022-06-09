from http import HTTPStatus
# from multiprocessing.connection import Client
from django.test import TestCase, override_settings, Client
from django.contrib.auth.models import User
from django.urls import reverse
from purchases.models import Department, PurchaseRequest, Product, Requisitioner, SpendCategory, Urgency, Vendor
from model_bakery import baker
from django.contrib.auth.models import Permission

from web_project.settings import AFTERSHIP_WEBHOOK_SECRET

class PurchaseRequestTestModel(TestCase):

    def setUp(self):
        # print("something")
        user_department = baker.make(Department, code='SEAS')
        user = baker.make(User)
        print("User department code: " + user.department.code)
        requisitioner = baker.make(Requisitioner, user=user, phone='5091234567')
        print('something else')
        print(requisitioner.phone)
        baker.make(Urgency, name='Standard')
        vendor = baker.make(Vendor, name='Tormach')
        print(vendor.name)
        print(user_department.name)
        self.purchase_request = baker.make(PurchaseRequest,vendor=vendor,requisitioner=requisitioner)
        self.purchase_request = PurchaseRequest.objects.get(pk=self.purchase_request.pk)

    def test_using_purchase_request(self):
        self.assertIsInstance(self.purchase_request, PurchaseRequest)
        # self.assertIsNotNone(self.purchase_request.slug)
        self.assertNotEqual(self.purchase_request.slug, "")

class TestCreatePRView(TestCase):

    def setUp(self):
        baker.make(Department, code='SEAS')
        self.user = baker.make(User)

    def test_anonymous_cannot_see_page(self):
        response = self.client.get(reverse("new_pr"))
        self.assertRedirects(response, "/accounts/login/?next=/new-purchase-request/")

    def test_permissed_user_can_see_page(self):
        # user = baker.make(User)
        self.user.user_permissions.add(Permission.objects.get(codename='add_purchaserequest'))
        
        self.client.force_login(user=self.user)
        response = self.client.get(reverse("new_pr"))
        self.assertEqual(response.status_code, 200)

@override_settings(AFTERSHIP_WEBHOOK_SECRET="abc123")
class TrackingWebhookTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)

    def test_bad_method(self):
        response = self.client.get("webhooks/tracking/&@0k6sCB8M40NNWydUwn%j$egfzlPgqG/")

        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED