from django.test import TestCase
from django.urls import reverse


# Create your tests here.
class HomeTemplateTests(TestCase):

    def test_mailchimp_script_is_not_loaded(self):
        """Check if the Mailchimp script is not loaded"""
        response = self.client.get(reverse("home"))

        self.assertNotContains(response, "chimpstatic.com")

    def test_home_page_displays_b2b_information(self):
        """Check if the home page explains who the shop is for"""
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Created for demonstration purposes, intended for dental "
            "practices, dental laboratories and other dental businesses",
        )

    def test_privacy_policy_uses_current_document(self):
        """Check if the current privacy policy document is displayed"""
        response = self.client.get(reverse("privacy_policy"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["documents"],
            [
                {
                    "name": "Privacy and Cookies Policy",
                    "file": "bbdental-privacy-and-cookies-policy.pdf",
                }
            ],
        )
        self.assertContains(
            response,
            "documents/bbdental-privacy-and-cookies-policy.pdf",
        )
        self.assertContains(
            response,
            '<h1 class="fw-bold">Privacy and Cookies Policy</h1>',
            html=True,
        )
        self.assertContains(response, "Open document (PDF)")
        self.assertContains(
            response,
            'aria-label="Open Privacy and Cookies Policy PDF"',
        )

    def test_terms_of_service_uses_current_document(self):
        """Check if the current terms and conditions document is displayed"""
        response = self.client.get(reverse("terms_of_service"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["documents"],
            [
                {
                    "name": "Terms and Conditions",
                    "file": "bbdental-terms-and-conditions.pdf",
                }
            ],
        )
        self.assertContains(
            response,
            "documents/bbdental-terms-and-conditions.pdf",
        )
        self.assertContains(
            response,
            '<h1 class="fw-bold">Terms and Conditions</h1>',
            html=True,
        )
        self.assertContains(response, "Open document (PDF)")
        self.assertContains(
            response,
            'aria-label="Open Terms and Conditions PDF"',
        )

    def test_contact_page_displays_current_contact_details(self):
        """Check if the contact page displays the current contact details"""
        response = self.client.get(reverse("contact_page"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "bbdental.shop@gmail.com")
        self.assertNotContains(response, "info@bbdental.shop")
        self.assertNotContains(response, "tel:")
        self.assertNotContains(response, "+01 234 567 89")
