from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from .forms import UserProfileForm
from checkout.models import Order


class ProfileViewsTests(TestCase):
    def setUp(self):
        """Create a user for profile tests"""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            first_name="John",
            last_name="Murphy",
            password="password123"
        )
        self.client.login(username="testuser", password="password123")

    def test_profile_displays_user_full_name(self):
        """Check if the profile page shows the user's full name"""
        response = self.client.get(reverse("profile"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "John Murphy")

    def test_profile_link_is_active(self):
        """Check if the profile link is active on the profile page"""
        response = self.client.get(reverse("profile"))

        self.assertContains(
            response,
            'class="d-flex flex-column align-items-center text-center link '
            'active"'
        )

    def test_user_cannot_view_another_users_order(self):
        """Check if a user cannot view an order belonging to another user."""
        other_user = User.objects.create_user(
            username="otheruser",
            password="password123"
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
        )

        response = self.client.get(
            reverse("order_history", args=[other_order.order_number])
        )

        self.assertEqual(response.status_code, 404)

    def test_user_can_view_their_own_order(self):
        """Check if a user can view their own order."""
        order = Order.objects.create(
            user_profile=self.user.userprofile,
            name="John",
            surname="Murphy",
            email="john@example.com",
            phone_number="+353 87 123 4567",
            address_line_1="1 Main Street",
            town="Dublin",
            postcode="D24 ABC1",
            country="IE",
        )

        response = self.client.get(
            reverse("order_history", args=[order.order_number])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, order.order_number)
        self.assertContains(response, "Status:")
        self.assertContains(response, order.get_status_display())

    def test_profile_displays_order_status(self):
        """Check if the order status is displayed in the order history."""
        Order.objects.create(
            user_profile=self.user.userprofile,
            name="John",
            surname="Murphy",
            email="john@example.com",
            phone_number="+353 87 123 4567",
            address_line_1="1 Main Street",
            town="Dublin",
            postcode="D24 ABC1",
            country="IE",
            status="processing",
        )

        response = self.client.get(reverse("profile"))

        self.assertContains(response, "Status: Processing")


class UserProfileFormTests(TestCase):
    def test_address_line_3_is_not_in_profile_form(self):
        """Check if address_line_3 is not in UserProfileForm"""
        form = UserProfileForm()

        self.assertNotIn('default_address_line_3', form.fields)
