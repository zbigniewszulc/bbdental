from unittest.mock import patch

import json
from decimal import Decimal

from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.core import mail
from django.template.loader import render_to_string
from django.test import TestCase
from django.urls import reverse

from products.models import Category, Manufacturer, Product, Subcategory

from .emails import send_order_confirmation
from .forms import OrderForm, OrderStatusForm
from .models import Order, OrderLineItem
from .webhook_handler import StripeWH_Handler


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

    def test_order_status_form_only_contains_status(self):
        """Check if OrderStatusForm only contains the status field"""
        form = OrderStatusForm()

        self.assertEqual(list(form.fields), ['status'])


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

    def test_checkout_contains_stripe_pid_field(self):
        """Check if checkout contains the Stripe payment ID field."""
        html = render_to_string(
            "checkout/checkout.html",
            {"order_form": OrderForm()},
        )

        self.assertIn('name="stripe_pid"', html)

    def test_checkout_displays_bulk_unit_price(self):
        """Check if checkout displays the bulk unit price"""
        html = render_to_string(
            "checkout/checkout.html",
            {
                "order_form": OrderForm(),
                "bag_items": [
                    {
                        "product": {
                            "id": 1,
                            "product_name": "Bulk Product",
                            "picture_location": None,
                            "price": Decimal("20.00"),
                        },
                        "quantity": 5,
                        "unit_price": Decimal("15.00"),
                        "total_price": Decimal("75.00"),
                    }
                ],
                "total": Decimal("75.00"),
                "delivery": Decimal("0.00"),
                "free_delivery_delta": Decimal("0.00"),
                "grand_total": Decimal("75.00"),
            },
        )

        self.assertIn("€15.00 x 5", html)


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


class CheckoutBusinessNameTests(TestCase):
    def setUp(self):
        """Create a customer, profile and product for checkout tests"""
        self.user = User.objects.create_user(
            username="businesscustomer",
            password="password123",
            email="peter@example.com",
        )
        self.user.userprofile.business_name = "Dublin Dental Practice"
        self.user.userprofile.save()

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
        self.product = Product.objects.create(
            product_name="Test Product",
            description="Test product description",
            price=Decimal("15.00"),
            in_stock=10,
            manufacturer=manufacturer,
            subcategory=subcategory,
        )

        self.client.login(
            username="businesscustomer",
            password="password123",
        )

        session = self.client.session
        session["bag"] = {str(self.product.id): 1}
        session.save()

    def test_checkout_saves_business_name_from_profile(self):
        """Check if checkout saves the business name from the profile"""
        response = self.client.post(
            reverse("checkout"),
            {
                "name": "Peter",
                "surname": "Byrne",
                "email": "peter@example.com",
                "phone_number": "+353 86 123 4567",
                "address_line_1": "47 Virginia Hall",
                "address_line_2": "Belgard Square",
                "town": "Tallaght",
                "postcode": "D24 ABC1",
                "country": "IE",
            },
        )

        order = Order.objects.get(
            user_profile=self.user.userprofile
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            order.business_name,
            "Dublin Dental Practice",
        )


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

    def test_new_order_has_new_status_by_default(self):
        """Check if a new order has New status by default."""
        order = Order.objects.create(
            name="Peter",
            surname="Byrne",
            email="peter@example.com",
            phone_number="+353 87 123 4567",
            address_line_1="47 Virginia Hall",
            town="Tallaght",
            postcode="D24 ABC1",
            country="IE",
        )

        self.assertEqual(order.status, "new")

    def test_order_can_store_business_name(self):
        """Check if an order can store a business name"""
        order = Order.objects.create(
            name="Peter",
            surname="Byrne",
            email="peter@example.com",
            phone_number="+353 86 123 4567",
            address_line_1="47 Virginia Hall",
            town="Tallaght",
            postcode="D24 ABC1",
            country="IE",
            business_name="Dublin Dental Practice",
        )

        self.assertEqual(
            order.business_name,
            "Dublin Dental Practice"
        )

    def test_order_line_item_uses_bulk_price(self):
        """Check if order line item uses bulk price"""
        category = Category.objects.create(
            category_name="Test Category",
        )
        subcategory = Subcategory.objects.create(
            subcategory_name="Test Subcategory",
            category=category,
        )
        manufacturer = Manufacturer.objects.create(
            manufacturer_name="Test Manufacturer",
        )
        product = Product.objects.create(
            product_name="Bulk Product",
            description="Test product",
            price=Decimal("20.00"),
            bulk_quantity=5,
            bulk_price=Decimal("15.00"),
            in_stock=100,
            manufacturer=manufacturer,
            subcategory=subcategory,
        )
        order = Order.objects.create(
            name="Peter",
            surname="Byrne",
            email="peter@example.com",
            phone_number="+353 87 123 4567",
            address_line_1="47 Virginia Hall",
            town="Tallaght",
            postcode="D24 ABC1",
            country="IE",
        )

        line_item = OrderLineItem.objects.create(
            order=order,
            product=product,
            quantity=5,
        )

        self.assertEqual(line_item.line_item_total, Decimal("75.00"))


class CheckoutCacheDataTests(TestCase):
    def setUp(self):
        """Create and log in a customer."""
        self.user = User.objects.create_user(
            username="testcustomer",
            password="password123",
        )
        self.client.login(
            username="testcustomer",
            password="password123",
        )

    def test_cache_checkout_data_requires_client_secret(self):
        """Check if client secret is required."""
        response = self.client.post(reverse("cache_checkout_data"))

        self.assertEqual(response.status_code, 400)

    @patch("checkout.views.stripe.PaymentIntent.modify")
    def test_invalid_checkout_data_is_rejected_before_payment(
        self,
        mock_payment_intent_modify,
    ):
        """Check if invalid checkout data is rejected before payment."""
        response = self.client.post(
            reverse("cache_checkout_data"),
            {
                "client_secret": "pi_test_123_secret_test",
                "save_profile": "false",
                "name": "Gianluca",
                "surname": "Yoris",
                "email": "customer@example.com",
                "phone_number": "23 O'Connell Street",
                "address_line_1": "Dublin 1",
                "address_line_2": "",
                "town": "Dublin",
                "postcode": "D01 X285",
                "country": "IE",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertContains(
            response,
            "Enter a valid phone number.",
            status_code=400,
        )
        mock_payment_intent_modify.assert_not_called()


class CheckoutWebhookHandlerTests(TestCase):
    def test_success_handler_finds_existing_order(self):
        """Check if an existing order is not created again."""
        Order.objects.create(
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

        event = {
            "type": "payment_intent.succeeded",
            "data": {
                "object": {
                    "id": "pi_test_123",
                },
            },
        }

        # This calls the handler directly without an HTTP request
        handler = StripeWH_Handler(None)
        response = handler.handle_payment_intent_succeeded(event)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Order already exists")
        self.assertEqual(
            Order.objects.filter(stripe_pid="pi_test_123").count(),
            1,
        )

    def test_success_handler_creates_order_and_saves_profile(self):
        """Check if the webhook creates an order and saves delivery details
        for a new payment."""
        user = User.objects.create_user(
            username="testcustomer",
            password="password123",
            email="peter@example.com",
        )
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
        product = Product.objects.create(
            product_name="Test Product",
            description="Test product description",
            price=Decimal("15.00"),
            bulk_quantity=2,
            bulk_price=Decimal("12.00"),
            in_stock=10,
            manufacturer=manufacturer,
            subcategory=subcategory,
        )

        user.userprofile.business_name = "Dublin Dental Practice"
        user.userprofile.save()

        event = {
            "type": "payment_intent.succeeded",
            "data": {
                "object": {
                    "id": "pi_test_new",
                    "metadata": {
                        "bag": json.dumps({str(product.id): 2}),
                        "user_id": str(user.id),
                        "save_profile": "true",
                    },
                    "shipping": {
                        "name": "Peter Byrne",
                        "phone": "+353 87 123 4567",
                        "address": {
                            "line1": "47 Virginia Hall",
                            "line2": "Belgard Square",
                            "city": "Tallaght",
                            "postal_code": "D24 ABC1",
                            "country": "IE",
                        },
                    },
                },
            },
        }

        handler = StripeWH_Handler(None)
        response = handler.handle_payment_intent_succeeded(event)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Order.objects.filter(stripe_pid="pi_test_new").exists()
        )

        order = Order.objects.get(stripe_pid="pi_test_new")
        line_item = OrderLineItem.objects.get(order=order)

        self.assertEqual(order.business_name, "Dublin Dental Practice")
        self.assertEqual(line_item.product, product)
        self.assertEqual(line_item.quantity, 2)
        self.assertEqual(line_item.line_item_total, Decimal("24.00"))
        self.assertEqual(order.subtotal, Decimal("24.00"))

        user.refresh_from_db()
        profile = user.userprofile
        profile.refresh_from_db()

        self.assertEqual(user.first_name, "Peter")
        self.assertEqual(user.last_name, "Byrne")
        self.assertEqual(
            profile.default_phone_number,
            "+353 87 123 4567",
        )
        self.assertEqual(
            profile.default_address_line_1,
            "47 Virginia Hall",
        )
        self.assertEqual(
            profile.default_address_line_2,
            "Belgard Square",
        )
        self.assertEqual(profile.default_town, "Tallaght")
        self.assertEqual(profile.default_postcode, "D24 ABC1")
        self.assertEqual(profile.default_country.code, "IE")

        # Check that one confirmation email is sent to the customer
        # and includes the ordered product
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["peter@example.com"])
        self.assertIn("Test Product", mail.outbox[0].body)

    def test_success_handler_does_not_keep_incomplete_order(self):
        """Check if an incomplete order is removed when a product is missing"""
        user = User.objects.create_user(
            username="testcustomer2",
            password="password123",
            email="peter@example.com",
        )

        user.userprofile.business_name = "Dublin Dental Practice"
        user.userprofile.save()

        event = {
            "type": "payment_intent.succeeded",
            "data": {
                "object": {
                    "id": "pi_missing_product",
                    "metadata": {
                        "bag": json.dumps({"999999": 1}),
                        "user_id": str(user.id),
                        "save_profile": "false",
                    },
                    "shipping": {
                        "name": "Peter Byrne",
                        "phone": "+353 87 123 4567",
                        "address": {
                            "line1": "47 Virginia Hall",
                            "line2": "Belgard Square",
                            "city": "Tallaght",
                            "postal_code": "D24 ABC1",
                            "country": "IE",
                        },
                    },
                },
            },
        }

        handler = StripeWH_Handler(None)
        response = handler.handle_payment_intent_succeeded(event)

        self.assertEqual(response.status_code, 500)
        self.assertFalse(
            Order.objects.filter(
                stripe_pid="pi_missing_product"
            ).exists()
        )
        self.assertEqual(len(mail.outbox), 0)

    def test_failed_handler_does_not_create_order(self):
        """Check if a failed payment does not create an order."""
        event = {
            "type": "payment_intent.payment_failed",
            "data": {
                "object": {
                    "id": "pi_test_failed",
                },
            },
        }

        handler = StripeWH_Handler(None)
        response = handler.handle_payment_intent_payment_failed(event)

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "payment_intent.payment_failed",
        )
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)


class CheckoutExistingOrderTests(TestCase):
    def setUp(self):
        """Create a customer and an existing order."""
        self.user = User.objects.create_user(
            username="testcustomer",
            password="password123",
        )
        self.client.login(
            username="testcustomer",
            password="password123",
        )

        self.order = Order.objects.create(
            user_profile=self.user.userprofile,
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

    def test_checkout_uses_order_created_by_webhook(self):
        """Check if checkout uses an order created by the webhook."""
        response = self.client.post(
            reverse("checkout"),
            # Data sent in the request. It corresponds to the form field
            {"stripe_pid": "pi_test_123"},
        )

        self.assertRedirects(
            response,
            reverse(
                "checkout_success",
                args=[self.order.order_number],
            ),
            # Check the redirect URL without loading the destination
            # page because only the redirect itself is tested
            fetch_redirect_response=False,
        )
        self.assertEqual(
            Order.objects.filter(stripe_pid="pi_test_123").count(),
            1,
        )

    def test_checkout_redirects_to_paid_order_saved_in_session(self):
        """Check if returning to checkout opens the completed order."""
        session = self.client.session
        session['bag'] = {'1': 2}
        session['stripe_pid'] = 'pi_test_123'
        session.save()

        response = self.client.get(reverse("checkout"))

        self.assertRedirects(
            response,
            reverse(
                "checkout_success",
                args=[self.order.order_number],
            ),
        )

        self.assertNotIn('bag', self.client.session)
        self.assertNotIn('stripe_pid', self.client.session)

    def test_user_cannot_view_another_users_checkout_success(self):
        """Check if a user cannot view another user's completed order."""
        other_user = User.objects.create_user(
            username="othercustomer",
            password="password123",
        )

        other_order = Order.objects.create(
            user_profile=other_user.userprofile,
            name="Conor",
            surname="Murphy",
            email="conor@example.com",
            phone_number="+353 87 123 4567",
            address_line_1="1 Main Street",
            town="Dublin",
            postcode="D24 ABC1",
            country="IE",
            stripe_pid="pi_test_other",
        )

        response = self.client.get(
            reverse(
                "checkout_success",
                args=[other_order.order_number],
            )
        )

        self.assertEqual(response.status_code, 404)


class ManageOrdersTests(TestCase):
    def setUp(self):
        """Create and log in a staff user"""
        self.staff_user = User.objects.create_user(
            username="staffuser",
            password="password123",
            is_staff=True,
        )
        self.client.login(
            username="staffuser",
            password="password123",
        )

    def test_staff_user_can_access_order_management(self):
        """Check if a staff user can access order management"""
        response = self.client.get(reverse("manage_orders"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Order Management")

    def test_customer_cannot_access_order_management(self):
        """Check if a customer cannot access order management"""
        self.client.logout()

        User.objects.create_user(
            username="customer",
            password="password123",
        )
        self.client.login(
            username="customer",
            password="password123",
        )

        response = self.client.get(reverse("manage_orders"))

        self.assertRedirects(
            response,
            f'{reverse("admin:login")}?next={reverse("manage_orders")}',
        )

    def test_orders_are_listed_newest_first(self):
        """Check if the newest orders are displayed first"""
        customer = User.objects.create_user(
            username="customer",
            password="password123",
        )

        first_order = Order.objects.create(
            user_profile=customer.userprofile,
            name="Peter",
            surname="Byrne",
            email="peter@example.com",
            phone_number="+353 87 123 4567",
            address_line_1="47 Virginia Hall",
            town="Tallaght",
            postcode="D24 ABC1",
            country="IE",
        )

        second_order = Order.objects.create(
            user_profile=customer.userprofile,
            name="Conor",
            surname="Murphy",
            email="conor@example.com",
            phone_number="+353 87 765 4321",
            address_line_1="1 Main Street",
            town="Dublin",
            postcode="D24 ABC2",
            country="IE",
        )

        response = self.client.get(reverse("manage_orders"))

        self.assertEqual(
            list(response.context["page_obj"]),
            [second_order, first_order],
        )

    def test_order_management_displays_order_details(self):
        """Check if order details are displayed for staff users"""
        customer = User.objects.create_user(
            username="ordercustomer",
            password="password123",
        )

        order = Order.objects.create(
            user_profile=customer.userprofile,
            business_name="Dublin Dental Practice",
            name="Peter",
            surname="Byrne",
            email="peter@example.com",
            phone_number="+353 87 123 4567",
            address_line_1="47 Virginia Hall",
            town="Tallaght",
            postcode="D24 ABC1",
            country="IE",
            grand_total=Decimal("50.00"),
            status="processing",
        )

        response = self.client.get(reverse("manage_orders"))

        self.assertContains(response, order.order_number)
        self.assertContains(response, "Dublin Dental Practice")
        self.assertContains(response, "Peter Byrne")
        self.assertContains(response, "€50.00")
        self.assertContains(response, "Processing")

    def test_staff_user_sees_order_management_link(self):
        """Check if staff users see the order management link"""
        response = self.client.get(reverse("manage_orders"))

        self.assertContains(
            response,
            f'href="{reverse("manage_orders")}"',
        )

    def test_staff_user_can_view_order_details(self):
        """Check if a staff user can view order details"""
        customer = User.objects.create_user(
            username="detailcustomer",
            password="password123",
        )

        order = Order.objects.create(
            user_profile=customer.userprofile,
            business_name="Dublin Dental Practice",
            name="Peter",
            surname="Byrne",
            email="peter@example.com",
            phone_number="+353 87 123 4567",
            address_line_1="47 Virginia Hall",
            town="Tallaght",
            postcode="D24 ABC1",
            country="IE",
        )

        response = self.client.get(
            reverse(
                "order_management_details",
                args=[order.order_number],
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, order.order_number)
        self.assertContains(response, "Peter Byrne")
        self.assertContains(response, "Dublin Dental Practice")
        self.assertContains(response, "peter@example.com")
        self.assertContains(response, "+353 87 123 4567")
        self.assertContains(response, "47 Virginia Hall")
        self.assertContains(response, "Tallaght")
        self.assertContains(response, "New")
        self.assertContains(response, 'name="status"')
        self.assertContains(response, "Back to Order Management")

    def test_customer_cannot_view_order_management_details(self):
        """Check if a customer cannot view staff order details"""
        customer = User.objects.create_user(
            username="customer",
            password="password123",
        )

        order = Order.objects.create(
            user_profile=customer.userprofile,
            name="Peter",
            surname="Byrne",
            email="peter@example.com",
            phone_number="+353 87 123 4567",
            address_line_1="47 Virginia Hall",
            town="Tallaght",
            postcode="D24 ABC1",
            country="IE",
        )

        self.client.logout()
        self.client.login(
            username="customer",
            password="password123",
        )

        response = self.client.get(
            reverse(
                "order_management_details",
                args=[order.order_number],
            )
        )

        self.assertRedirects(
            response,
            (
                f'{reverse("admin:login")}?next='
                f'{reverse("order_management_details",
                           args=[order.order_number])}'
            ),
        )

    def test_order_management_contains_details_link(self):
        """Check if order management contains a details link"""
        customer = User.objects.create_user(
            username="linkcustomer",
            password="password123",
        )

        order = Order.objects.create(
            user_profile=customer.userprofile,
            name="Peter",
            surname="Byrne",
            email="peter@example.com",
            phone_number="+353 87 123 4567",
            address_line_1="47 Virginia Hall",
            town="Tallaght",
            postcode="D24 ABC1",
            country="IE",
        )

        response = self.client.get(reverse("manage_orders"))

        self.assertContains(
            response,
            reverse(
                "order_management_details",
                args=[order.order_number],
            ),
        )

    def test_order_details_display_items_and_summary(self):
        """Check if order items and totals are displayed"""
        customer = User.objects.create_user(
            username="itemcustomer",
            password="password123",
        )
        category = Category.objects.create(
            category_name="Test Category",
        )
        subcategory = Subcategory.objects.create(
            subcategory_name="Test Subcategory",
            category=category,
        )
        manufacturer = Manufacturer.objects.create(
            manufacturer_name="Test Manufacturer",
        )
        product = Product.objects.create(
            product_name="Test Product",
            description="Test product description",
            price=Decimal("20.00"),
            in_stock=10,
            manufacturer=manufacturer,
            subcategory=subcategory,
        )
        order = Order.objects.create(
            user_profile=customer.userprofile,
            name="Peter",
            surname="Byrne",
            email="peter@example.com",
            phone_number="+353 87 123 4567",
            address_line_1="47 Virginia Hall",
            town="Tallaght",
            postcode="D24 ABC1",
            country="IE",
        )
        line_item = OrderLineItem.objects.create(
            order=order,
            product=product,
            quantity=2,
        )
        # Reload the order because saving a line item updates its subtotal,
        # delivery cost and grand total
        order.refresh_from_db()

        response = self.client.get(
            reverse(
                "order_management_details",
                args=[order.order_number],
            )
        )

        self.assertContains(response, "Test Product")
        self.assertContains(response, "2")
        self.assertContains(
            response,
            f'€{line_item.line_item_total:.2f}',
        )
        self.assertContains(response, f'€{order.subtotal:.2f}')
        self.assertContains(response, f'€{order.delivery_cost:.2f}')
        self.assertContains(response, f'€{order.grand_total:.2f}')

    def test_staff_user_can_update_order_status(self):
        """Check if a staff user can update an order status"""
        customer = User.objects.create_user(
            username="statuscustomer",
            password="password123",
        )
        order = Order.objects.create(
            user_profile=customer.userprofile,
            name="Peter",
            surname="Byrne",
            email="peter@example.com",
            phone_number="+353 87 123 4567",
            address_line_1="47 Virginia Hall",
            town="Tallaght",
            postcode="D24 ABC1",
            country="IE",
        )

        response = self.client.post(
            reverse(
                "order_management_details",
                args=[order.order_number],
            ),
            # Send the new order status in the form data
            {'status': 'processing'},
        )

        self.assertRedirects(
            response,
            reverse(
                "order_management_details",
                args=[order.order_number],
            ),
        )

        # Convert stored messages into a list
        messages = list(get_messages(response.wsgi_request))

        # Check the success message shown to the staff user
        self.assertEqual(
            str(messages[0]),
            'Order status updated successfully',
        )

        order.refresh_from_db()

        self.assertEqual(order.status, 'processing')

    def test_updated_status_is_displayed_to_customer(self):
        """Check if an updated status is displayed to the customer"""
        customer = User.objects.create_user(
            username="historycustomer",
            password="password123",
        )
        order = Order.objects.create(
            user_profile=customer.userprofile,
            name="Peter",
            surname="Byrne",
            email="peter@example.com",
            phone_number="+353 87 123 4567",
            address_line_1="47 Virginia Hall",
            town="Tallaght",
            postcode="D24 ABC1",
            country="IE",
        )

        response = self.client.post(
            reverse(
                "order_management_details",
                args=[order.order_number],
            ),
            {'status': 'processing'},
        )

        self.assertRedirects(
            response,
            reverse(
                "order_management_details",
                args=[order.order_number],
            ),
        )

        self.client.logout()
        self.client.login(
            username="historycustomer",
            password="password123",
        )

        response = self.client.get(reverse("profile"))

        self.assertContains(response, "Status: Processing")

    def test_order_management_is_paginated(self):
        """Check if order management shows 70 orders per page"""
        customer = User.objects.create_user(
            username="paginationcustomer",
            password="password123",
        )

        for number in range(71):
            Order.objects.create(
                user_profile=customer.userprofile,
                name="Peter",
                surname="Byrne",
                email="peter@example.com",
                phone_number="+353 87 123 4567",
                address_line_1=f"{number} Main Street",
                town="Tallaght",
                postcode="D24 ABC1",
                country="IE",
            )

        response = self.client.get(
            reverse("manage_orders"),
            {"page": 2},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["page_obj"]), 1)

    def test_staff_user_can_search_orders_by_order_number(self):
        """Check if staff users can search by a partial order number"""
        customer = User.objects.create_user(
            username="searchcustomer",
            password="password123",
        )

        matching_order = Order.objects.create(
            order_number="SEARCH123ABC",
            user_profile=customer.userprofile,
            name="Peter",
            surname="Byrne",
            email="peter@example.com",
            phone_number="+353 87 123 4567",
            address_line_1="47 Virginia Hall",
            town="Tallaght",
            postcode="D24 ABC1",
            country="IE",
        )

        # Add another order so the test can confirm that non-matching
        # order numbers are not included in the search results
        Order.objects.create(
            order_number="OTHER456DEF",
            user_profile=customer.userprofile,
            name="Conor",
            surname="Murphy",
            email="conor@example.com",
            phone_number="+353 87 765 4321",
            address_line_1="1 Main Street",
            town="Dublin",
            postcode="D24 ABC2",
            country="IE",
        )

        response = self.client.get(
            reverse("manage_orders"),
            {"order_number": "SEARCH123"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["page_obj"]),
            [matching_order],
        )

    def test_order_search_is_kept_in_pagination_links(self):
        """Check if order search stays active when changing pages"""
        customer = User.objects.create_user(
            username="searchpaginationcustomer",
            password="password123",
        )

        for number in range(71):
            Order.objects.create(
                order_number=f"SEARCH{number}",
                user_profile=customer.userprofile,
                name="Peter",
                surname="Byrne",
                email="peter@example.com",
                phone_number="+353 87 123 4567",
                address_line_1=f"{number} Main Street",
                town="Tallaght",
                postcode="D24 ABC1",
                country="IE",
            )

        response = self.client.get(
            reverse("manage_orders"),
            {"order_number": "SEARCH"},
        )

        self.assertContains(
            response,
            '?page=2&order_number=SEARCH',
        )

    def test_staff_user_can_filter_orders_by_status(self):
        """Check if staff users can filter orders by status"""
        customer = User.objects.create_user(
            username="filtercustomer",
            password="password123",
        )

        matching_order = Order.objects.create(
            user_profile=customer.userprofile,
            name="Peter",
            surname="Byrne",
            email="peter@example.com",
            phone_number="+353 87 123 4567",
            address_line_1="47 Virginia Hall",
            town="Tallaght",
            postcode="D24 ABC1",
            country="IE",
            status="processing",
        )

        # Add another order to confirm that a different status is excluded
        Order.objects.create(
            user_profile=customer.userprofile,
            name="Conor",
            surname="Murphy",
            email="conor@example.com",
            phone_number="+353 87 765 4321",
            address_line_1="1 Main Street",
            town="Dublin",
            postcode="D24 ABC2",
            country="IE",
            status="new",
        )

        response = self.client.get(
            reverse("manage_orders"),
            {"status": "processing"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["page_obj"]),
            [matching_order],
        )

    def test_order_status_filter_is_kept_in_pagination_links(self):
        """Check if status filter stays active when changing pages"""
        customer = User.objects.create_user(
            username="statuspaginationcustomer",
            password="password123",
        )

        for number in range(71):
            Order.objects.create(
                order_number=f"PROCESSING{number}",
                user_profile=customer.userprofile,
                name="Peter",
                surname="Byrne",
                email="peter@example.com",
                phone_number="+353 87 123 4567",
                address_line_1=f"{number} Main Street",
                town="Tallaght",
                postcode="D24 ABC1",
                country="IE",
                status="processing",
            )

        response = self.client.get(
            reverse("manage_orders"),
            {"status": "processing"},
        )

        self.assertContains(
            response,
            "?page=2&order_number=&status=processing",
        )

    def test_search_and_status_filter_can_be_used_together(self):
        """Check if order search and status filter work together"""
        customer = User.objects.create_user(
            username="combinedfiltercustomer",
            password="password123",
        )

        matching_order = Order.objects.create(
            order_number="SEARCHPROCESSING",
            user_profile=customer.userprofile,
            name="Peter",
            surname="Byrne",
            email="peter@example.com",
            phone_number="+353 87 123 4567",
            address_line_1="47 Virginia Hall",
            town="Tallaght",
            postcode="D24 ABC1",
            country="IE",
            status="processing",
        )

        # This order matches the search but has a different status
        Order.objects.create(
            order_number="SEARCHNEW",
            user_profile=customer.userprofile,
            name="Conor",
            surname="Murphy",
            email="conor@example.com",
            phone_number="+353 87 765 4321",
            address_line_1="1 Main Street",
            town="Dublin",
            postcode="D24 ABC2",
            country="IE",
            status="new",
        )

        # This order has the correct status but does not match the search
        Order.objects.create(
            order_number="OTHERPROCESSING",
            user_profile=customer.userprofile,
            name="Anna",
            surname="Kelly",
            email="anna@example.com",
            phone_number="+353 87 111 2233",
            address_line_1="2 Main Street",
            town="Dublin",
            postcode="D24 ABC3",
            country="IE",
            status="processing",
        )

        response = self.client.get(
            reverse("manage_orders"),
            {
                "order_number": "SEARCH",
                "status": "processing",
            },
        )

        self.assertEqual(
            list(response.context["page_obj"]),
            [matching_order],
        )

    def test_no_orders_message_is_displayed_for_empty_results(self):
        """Check if the no orders message appears when no orders match"""
        response = self.client.get(
            reverse("manage_orders"),
            {
                "order_number": "NOTFOUND",
                "status": "processing",
            },
        )

        self.assertContains(response, "No orders found.")
