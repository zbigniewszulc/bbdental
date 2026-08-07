from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse
from .forms import OrderForm


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

        # https://www.edureka.co/community/81432/how-can-i-unit-test-django-messages
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


class CheckoutFormTests(TestCase):
    def test_address_line_3_is_not_in_order_form(self):
        """Check if address_line_3 is not in OrderForm"""
        form = OrderForm()

        self.assertNotIn('address_line_3', form.fields)

    def test_postcode_is_required(self):
        """Check if postcode field is mandatory on the OrderForm"""
        form = OrderForm()

        self.assertTrue(form.fields['postcode'].required)


class CheckoutTemplateTests(TestCase):
    def test_checkout_contains_billing_address_option(self):
        """Check if checkout contains billing address fields.
        Render_to_string used because the intention is to test the template"""
        html = render_to_string(
            "checkout/checkout.html",
            {"order_form": OrderForm()}
        )

        self.assertIn('id="sameBillingAddress"', html)
        self.assertIn('id="billing-address-fields"', html)
        self.assertIn(
            "Billing address is the same as delivery address",
            html,
        )
