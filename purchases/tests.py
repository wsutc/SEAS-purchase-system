from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from purchases.models import PurchaseRequest, Product, SpendCategory, Urgency, Vendor
from model_bakery import baker
from django.contrib.auth.models import Permission

class PurchaseRequestTestModel(TestCase):

    def setUp(self):
        # print("something")
        user = baker.make(User)
        baker.make(Urgency, name='Standard')
        vendor = baker.make(Vendor, name='Tormach')
        self.purchase_request = baker.make(PurchaseRequest,vendor=vendor,requisitioner__user=user,requisitioner__phone='5091234567')
        self.purchase_request = PurchaseRequest.objects.get(pk=self.purchase_request.pk)

    def test_using_purchase_request(self):
        self.assertIsInstance(self.purchase_request, PurchaseRequest)
        # self.assertIsNotNone(self.purchase_request.slug)
        self.assertNotEqual(self.purchase_request.slug, "")

class TestCreatePRView(TestCase):

    def test_anonymous_cannot_see_page(self):
        response = self.client.get(reverse("new_pr"))
        self.assertRedirects(response, "/accounts/login/?next=/new-purchase-request/")

    def test_permissed_user_can_see_page(self):
        user = baker.make(User)
        user.user_permissions.add(Permission.objects.get(codename='add_purchaserequest'))
        
        self.client.force_login(user=user)
        response = self.client.get(reverse("new_pr"))
        self.assertEqual(response.status_code, 200)