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


class ProductManagementViewsTests(TestCase):
    def setUp(self):
        """Create product data and log in a staff user"""
        category = Category.objects.create(
            category_name="Test Category",
        )
        self.subcategory = Subcategory.objects.create(
            subcategory_name="Test Subcategory",
            category=category,
        )
        self.manufacturer = Manufacturer.objects.create(
            manufacturer_name="Test Manufacturer",
        )
        self.staff_user = User.objects.create_user(
            username="managementstaff",
            password="password123",
            is_staff=True,
        )
        self.client.login(
            username="managementstaff",
            password="password123",
        )

    def test_staff_user_can_search_products_by_name(self):
        """Check if staff users can search products by name"""
        matching_product = Product.objects.create(
            product_name="Single Bond",
            description="Dental adhesive",
            price=Decimal("20.00"),
            in_stock=10,
            manufacturer=self.manufacturer,
            subcategory=self.subcategory,
        )

        # Add another product with the search value only in its description
        # to confirm that this search checks product names only
        Product.objects.create(
            product_name="Dental Mirror",
            description="Bond application product",
            price=Decimal("5.00"),
            in_stock=20,
            manufacturer=self.manufacturer,
            subcategory=self.subcategory,
        )

        response = self.client.get(
            reverse("manage_products"),
            {"q": "bond"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["page_obj"]),
            [matching_product],
        )

    def test_product_name_search_is_kept_in_pagination_links(self):
        """Check if product name search stays active when changing pages"""
        for number in range(21):
            Product.objects.create(
                product_name=f"Bond Product {number}",
                description="Test product",
                price=Decimal("10.00"),
                in_stock=10,
                manufacturer=self.manufacturer,
                subcategory=self.subcategory,
            )

        response = self.client.get(
            reverse("manage_products"),
            {"q": "Bond"},
        )

        self.assertContains(
            response,
            "?page=2&sort=name&direction=asc&manufacturer=&q=Bond",
        )
