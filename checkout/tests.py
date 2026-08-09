from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse
from .forms import OrderForm
from decimal import Decimal
from django.core import mail
from products.models import Category, Manufacturer, Product, Subcategory
from .emails import send_order_confirmation
from .models import Order, OrderLineItem


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


class CheckoutEmailTests(TestCase):
    def setUp(self):
        """Create an order with two products."""
        category = Category.objects.create(
            category_name="Test Category"
        )
        subcategory = Subcategory.objects.create(
            subcategory_name="Test Subcategory",
            category=category,
        )
        manufacturer = Manufacturer.objects.create(
            manufacturer_name="Test Manufacturer"
        )

        first_product = Product.objects.create(
            product_name="First Test Product",
            description="First test product description",
            price=Decimal("15.00"),
            in_stock=10,
            manufacturer=manufacturer,
            subcategory=subcategory,
        )
        second_product = Product.objects.create(
            product_name="Second Test Product",
            description="Second test product description",
            price=Decimal("37.00"),
            in_stock=10,
            manufacturer=manufacturer,
            subcategory=subcategory,
        )

        self.order = Order.objects.create(
            name="Peter",
            surname="Byrne",
            email="peter@example.com",
            phone_number="+353 87 123 4567",
            address_line_1="47 Virginia Hall",
            address_line_2="Belgard Square",
            town="Tallaght",
            postcode="D24 ABC1",
            country="IE",
        )

        OrderLineItem.objects.create(
            order=self.order,
            product=first_product,
            quantity=1,
        )
        OrderLineItem.objects.create(
            order=self.order,
            product=second_product,
            quantity=1,
        )

    def test_order_confirmation_sends_one_email(self):
        """Check if one email is sent for an order with two products."""
        send_order_confirmation(self.order)

        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox[0]
        self.assertIn("First Test Product", email.body)
        self.assertIn("Second Test Product", email.body)


class CheckoutWebhookTests(TestCase):
    def test_webhook_rejects_get_request(self):
        """Check if the webhook only accepts POST requests."""
        response = self.client.get(reverse("wh"))

        self.assertEqual(response.status_code, 405)

    def test_webhook_rejects_missing_signature(self):
        """Check if a request without a Stripe signature is rejected."""
        response = self.client.post(
            reverse("wh"),
            data="{}",  # Send an empty JSON object
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)


class CheckoutOrderModelTests(TestCase):
    def test_order_stores_stripe_details(self):
        """Check if an order stores its bag and Stripe payment ID."""
        order = Order.objects.create(
            name="Peter",
            surname="Byrne",
            email="peter@example.com",
            phone_number="+353 87 123 4567",
            address_line_1="47 Virginia Hall",
            address_line_2="Belgard Square",
            town="Tallaght",
            postcode="D24 ABC1",
            country="IE",
            original_bag='{"1": 2}',
            stripe_pid="pi_test_123",
        )

        order.refresh_from_db()

        self.assertEqual(order.original_bag, '{"1": 2}')
        self.assertEqual(order.stripe_pid, "pi_test_123")
