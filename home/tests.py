from django.test import TestCase
from django.urls import reverse


# Create your tests here.
class HomeTemplateTests(TestCase):

    def test_mailchimp_script_is_not_loaded(self):
        """Check if the Mailchimp script is not loaded"""
        response = self.client.get(reverse("home"))

        self.assertNotContains(response, "chimpstatic.com")
