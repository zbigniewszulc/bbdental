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

    def test_product_page_displays_bulk_pricing(self):
        """Check if bulk pricing is displayed on the product page"""
        self.product.bulk_quantity = 10
        self.product.bulk_price = Decimal("15.00")
        self.product.save()

        response = self.client.get(
            reverse("product_details", args=[self.product.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bulk Price:")
        self.assertContains(response, "€15.00")
        self.assertContains(response, "10 or more")

    def test_product_page_hides_unavailable_bulk_pricing(self):
        """Check if bulk pricing is hidden when it is not available"""
        response = self.client.get(
            reverse("product_details", args=[self.product.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Bulk Price:")


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

    def test_staff_user_can_sort_products_by_stock_low_to_high(self):
        """Check if staff users can sort products by stock from low to high"""
        low_stock_product = Product.objects.create(
            product_name="Low Stock Product",
            description="Test product",
            price=Decimal("10.00"),
            in_stock=5,
            manufacturer=self.manufacturer,
            subcategory=self.subcategory,
        )

        high_stock_product = Product.objects.create(
            product_name="High Stock Product",
            description="Test product",
            price=Decimal("10.00"),
            in_stock=20,
            manufacturer=self.manufacturer,
            subcategory=self.subcategory,
        )

        response = self.client.get(
            reverse("manage_products"),
            {
                "sort": "stock",
                "direction": "asc",
            },
        )

        # Check that products are ordered from the lowest to the highest stock
        self.assertEqual(
            list(response.context["page_obj"]),
            [low_stock_product, high_stock_product],
        )

    def test_staff_user_can_sort_products_by_stock_high_to_low(self):
        """Check if staff users can sort products by stock from high to low"""
        low_stock_product = Product.objects.create(
            product_name="Low Stock Product",
            description="Test product",
            price=Decimal("10.00"),
            in_stock=5,
            manufacturer=self.manufacturer,
            subcategory=self.subcategory,
        )

        high_stock_product = Product.objects.create(
            product_name="High Stock Product",
            description="Test product",
            price=Decimal("10.00"),
            in_stock=20,
            manufacturer=self.manufacturer,
            subcategory=self.subcategory,
        )

        response = self.client.get(
            reverse("manage_products"),
            {
                "sort": "stock",
                "direction": "desc",
            },
        )

        self.assertEqual(
            list(response.context["page_obj"]),
            [high_stock_product, low_stock_product],
        )

    def test_add_product_page_displays_bulk_pricing_fields(self):
        """Check if bulk pricing fields are displayed on add product page"""
        response = self.client.get(reverse("add_product"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="bulk_quantity"')
        self.assertContains(response, 'name="bulk_price"')

    def test_edit_product_page_displays_bulk_pricing_fields(self):
        """Check if bulk pricing fields are displayed on edit product page"""
        product = Product.objects.create(
            product_name="Bulk Product",
            description="Test product",
            price=Decimal("20.00"),
            bulk_quantity=10,
            bulk_price=Decimal("15.00"),
            in_stock=100,
            manufacturer=self.manufacturer,
            subcategory=self.subcategory,
        )

        response = self.client.get(reverse("edit_product", args=[product.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="bulk_quantity"')
        self.assertContains(response, 'name="bulk_price"')
