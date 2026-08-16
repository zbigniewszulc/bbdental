from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


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
