from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse


class CheckoutViewsTests(TestCase):
    def setUp(self):
        """Create a staff user for checkout tests"""
        self.user = User.objects.create_user(
            username="staffuser",
            password="password123",
            is_staff=True,
        )
        self.client.login(
            username="staffuser",
            password="password123",
        )

    def test_staff_user_cannot_access_checkout(self):
        """Check if staff user cannot access checkout"""
        response = self.client.get(reverse("checkout"))

        self.assertRedirects(response, reverse("all_products"))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            str(messages[0]),
            "Staff accounts cannot make purchases.",
        )

    def test_staff_user_cannot_access_checkout_success(self):
        """Check if staff user cannot access checkout success page"""
        response = self.client.get(
            reverse("checkout_success", args=["test-order-number"])
        )

        self.assertRedirects(response, reverse("all_products"))
