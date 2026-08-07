from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from .forms import UserProfileForm


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


class UserProfileFormTests(TestCase):
    def test_address_line_3_is_not_in_profile_form(self):
        """Check if address_line_3 is not in UserProfileForm"""
        form = UserProfileForm()

        self.assertNotIn('default_address_line_3', form.fields)
