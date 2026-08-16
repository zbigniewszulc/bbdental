from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from checkout.models import Order


# Create your tests here.
class StaffDashboardTests(TestCase):
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

    def test_staff_user_can_access_dashboard(self):
        """Check if a staff user can access the dashboard"""
        response = self.client.get(reverse("staff_dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sales Dashboard")

    def test_dashboard_displays_total_orders(self):
        """Check if the total number of orders is displayed"""
        Order.objects.create(
            business_name="Dental Practice One",
            name="Peter",
            surname="Byrne",
            email="peter@example.com",
            phone_number="+353 86 111 1111",
            address_line_1="1 Main Street",
            town="Dublin",
            postcode="D24 ABC1",
            country="IE",
        )
        Order.objects.create(
            business_name="Dental Practice Two",
            name="Conor",
            surname="Murphy",
            email="conor@example.com",
            phone_number="+353 86 222 2222",
            address_line_1="2 Main Street",
            town="Dublin",
            postcode="D24 ABC2",
            country="IE",
        )

        response = self.client.get(reverse("staff_dashboard"))

        self.assertEqual(response.context["total_orders"], 2)
        self.assertContains(response, "Total Orders")

    def test_dashboard_calculates_total_revenue(self):
        """Check if cancelled orders are excluded from total revenue"""
        Order.objects.create(
            business_name="Dental Practice One",
            name="Peter",
            surname="Byrne",
            email="peter@example.com",
            phone_number="+353 86 111 1111",
            address_line_1="1 Main Street",
            town="Dublin",
            postcode="D24 ABC1",
            country="IE",
            grand_total=Decimal("100.00"),
        )
        Order.objects.create(
            business_name="Dental Practice Two",
            name="Conor",
            surname="Murphy",
            email="conor@example.com",
            phone_number="+353 86 222 2222",
            address_line_1="2 Main Street",
            town="Dublin",
            postcode="D24 ABC2",
            country="IE",
            grand_total=Decimal("50.00"),
            status="cancelled",
        )

        response = self.client.get(reverse("staff_dashboard"))

        self.assertEqual(
            response.context["total_revenue"],
            Decimal("100.00"),
        )
        self.assertContains(response, "Total Revenue")
        self.assertContains(response, "€100.00")

    def test_customer_cannot_access_dashboard(self):
        """Check if a customer cannot access the dashboard"""
        self.client.logout()

        User.objects.create_user(
            username="customer",
            password="password123",
        )
        self.client.login(
            username="customer",
            password="password123",
        )

        response = self.client.get(reverse("staff_dashboard"))

        self.assertRedirects(
            response,
            f'{reverse("admin:login")}?next={reverse("staff_dashboard")}',
        )

    def test_dashboard_link_is_displayed_for_staff_user(self):
        """Check if the dashboard link is displayed for a staff user"""
        response = self.client.get(reverse("staff_dashboard"))

        self.assertContains(
            response,
            f'href="{reverse("staff_dashboard")}"',
        )
