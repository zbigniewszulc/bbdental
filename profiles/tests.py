from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from checkout.models import Order

from .forms import UserProfileForm
from .models import UserProfile


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

    def test_profile_cannot_remove_business_name(self):
        """Check if a user cannot remove their business name"""
        profile = self.user.userprofile
        profile.business_name = "Dublin Dental Practice"
        profile.save()

        response = self.client.post(
            reverse("profile"),
            {"business_name": ""},
        )

        profile.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            profile.business_name,
            "Dublin Dental Practice"
        )


class UserProfileFormTests(TestCase):
    def test_address_line_3_is_not_in_profile_form(self):
        """Check if address_line_3 is not in UserProfileForm"""
        form = UserProfileForm()

        self.assertNotIn('default_address_line_3', form.fields)

    def test_business_name_is_required_in_profile_form(self):
        """Check if a business name is required in the profile form"""
        form = UserProfileForm(data={})

        self.assertFalse(form.is_valid())
        self.assertIn("business_name", form.errors)


class UserProfileModelTests(TestCase):
    def test_profile_can_store_business_name(self):
        """Check if a profile can store a business name"""
        user = User.objects.create_user(
            username="businessuser",
            password="password123"
        )

        profile = user.userprofile
        profile.business_name = "Dublin Dental Practice"
        profile.save()
        # Get a new profile instance from the database to confirm that
        # business_name was saved as a model field, rather than only added
        # temporarily to the profile object used in this test.
        saved_profile = UserProfile.objects.get(pk=profile.pk)

        self.assertEqual(
            saved_profile.business_name,
            "Dublin Dental Practice"
        )


class BusinessSignupTests(TestCase):
    def test_signup_page_shows_business_name_field(self):
        """Check if the signup page shows a business name field"""
        # Open the signup page to check if it includes the business name field
        response = self.client.get(reverse("account_signup"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Business name")

    def test_signup_saves_business_name_to_profile(self):
        """Check if signup saves the business name to the user profile"""
        response = self.client.post(
            reverse("account_signup"),
            {
                "username": "newbusinessuser",
                "email": "newbusiness@example.com",
                "email2": "newbusiness@example.com",
                "password1": "VeryStrongPassword123!",
                "password2": "VeryStrongPassword123!",
                "business_name": "Dublin Dental Practice",
            },
        )

        user = User.objects.get(username="newbusinessuser")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            user.userprofile.business_name,
            "Dublin Dental Practice"
        )

    def test_signup_requires_business_name(self):
        """Check if signup requires a business name"""
        response = self.client.post(
            reverse("account_signup"),
            {
                "username": "missingbusinessname",
                "email": "missing@example.com",
                "email2": "missing@example.com",
                "password1": "VeryStrongPassword123!",
                "password2": "VeryStrongPassword123!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "business_name",
            response.context["form"].errors,
        )
        self.assertFalse(
            User.objects.filter(username="missingbusinessname").exists()
        )
