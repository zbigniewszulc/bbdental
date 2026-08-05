from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Category, Manufacturer, Product, Subcategory


class ProductDetailViewsTests(TestCase):
    def setUp(self):
        """Create a product and staff user for tests"""
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
            price=Decimal("20.00"),
            in_stock=10,
            manufacturer=manufacturer,
            subcategory=subcategory,
        )
        self.user = User.objects.create_user(
            username="staffuser",
            password="password123",
            is_staff=True,
        )
        self.client.login(
            username="staffuser",
            password="password123",
        )

    def test_staff_user_sees_disabled_purchase_options(self):
        """Check if staff user sees disabled purchase options"""
        response = self.client.get(
            reverse("product_details", args=[self.product.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "Staff accounts cannot make purchases."
        )
        self.assertContains(
            response, 'class="btn btn-secondary" disabled'
        )
        self.assertNotContains(response, 'action="/bag/add/')
