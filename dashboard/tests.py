from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from checkout.models import Order, OrderLineItem
from products.models import Category, Manufacturer, Product, Subcategory


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

    def test_dashboard_prepares_monthly_order_data(self):
        """Check if orders are grouped by month"""
        january_order = Order.objects.create(
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
        february_order = Order.objects.create(
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

        # date_of_order is set automatically, so different dates are added
        # here to test orders from two separate months
        Order.objects.filter(pk=january_order.pk).update(
            date_of_order=timezone.make_aware(
                datetime(2026, 1, 15, 12, 0),
            ),
        )
        Order.objects.filter(pk=february_order.pk).update(
            date_of_order=timezone.make_aware(
                datetime(2026, 2, 15, 12, 0),
            ),
        )

        response = self.client.get(reverse("staff_dashboard"))

        self.assertEqual(
            response.context["monthly_order_labels"],
            ["January 2026", "February 2026"],
        )
        self.assertEqual(
            response.context["monthly_order_totals"],
            [1, 1],
        )

    def test_dashboard_prepares_top_selling_products_data(self):
        """Check if products are ordered by the quantity sold"""
        category = Category.objects.create(
            category_name="Test Category",
        )
        subcategory = Subcategory.objects.create(
            subcategory_name="Test Subcategory",
            category=category,
        )
        manufacturer = Manufacturer.objects.create(
            manufacturer_name="Test Manufacturer",
        )
        product_one = Product.objects.create(
            subcategory=subcategory,
            manufacturer=manufacturer,
            product_name="Product One",
            description="Test product",
            price=Decimal("10.00"),
            in_stock=20,
        )
        product_two = Product.objects.create(
            subcategory=subcategory,
            manufacturer=manufacturer,
            product_name="Product Two",
            description="Test product",
            price=Decimal("20.00"),
            in_stock=20,
        )
        order = Order.objects.create(
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

        OrderLineItem.objects.create(
            order=order,
            product=product_one,
            quantity=2,
        )
        OrderLineItem.objects.create(
            order=order,
            product=product_two,
            quantity=5,
        )

        response = self.client.get(reverse("staff_dashboard"))

        self.assertEqual(
            list(response.context["top_selling_products"]),
            [
                {
                    "product__product_name": "Product Two",
                    "total_quantity": 5,
                },
                {
                    "product__product_name": "Product One",
                    "total_quantity": 2,
                },
            ],
        )
        self.assertEqual(
            response.context["top_selling_product_labels"],
            ["Product Two", "Product One"],
        )
        self.assertEqual(
            response.context["top_selling_product_totals"],
            [5, 2],
        )

    def test_dashboard_includes_low_stock_products(self):
        """Check if products below the stock limit are included"""
        category = Category.objects.create(
            category_name="Test Category",
        )
        subcategory = Subcategory.objects.create(
            subcategory_name="Test Subcategory",
            category=category,
        )
        manufacturer = Manufacturer.objects.create(
            manufacturer_name="Test Manufacturer",
        )
        low_stock_product = Product.objects.create(
            subcategory=subcategory,
            manufacturer=manufacturer,
            product_name="Low Stock Product",
            description="Test product",
            price=Decimal("10.00"),
            in_stock=5,
        )
        Product.objects.create(
            subcategory=subcategory,
            manufacturer=manufacturer,
            product_name="Available Product",
            description="Test product",
            price=Decimal("20.00"),
            in_stock=10,
        )

        response = self.client.get(reverse("staff_dashboard"))

        self.assertEqual(
            list(response.context["low_stock_products"]),
            [low_stock_product],
        )
        self.assertContains(response, "Low Stock Products")
        self.assertContains(response, "Low Stock Product")
        self.assertContains(response, "5 items left")

    def test_dashboard_displays_top_selling_products_chart(self):
        """Check if the top selling products chart is displayed"""
        response = self.client.get(reverse("staff_dashboard"))

        self.assertContains(response, "Top 5 Selling Products")
        self.assertContains(
            response,
            'id="top-selling-products-chart"',
        )

    def test_dashboard_includes_top_selling_product_data(self):
        """Check if top selling product data is included for the chart"""
        response = self.client.get(reverse("staff_dashboard"))

        self.assertContains(
            response,
            'id="top-selling-product-labels"',
        )
        self.assertContains(
            response,
            'id="top-selling-product-totals"',
        )

    def test_dashboard_displays_monthly_orders_chart(self):
        """Check if the monthly orders chart is displayed"""
        response = self.client.get(reverse("staff_dashboard"))

        self.assertContains(response, "Monthly Orders")
        self.assertContains(response, 'id="monthly-orders-chart"')

    def test_dashboard_includes_monthly_order_data(self):
        """Check if monthly order data is included for the chart"""
        response = self.client.get(reverse("staff_dashboard"))

        self.assertContains(response, 'id="monthly-order-labels"')
        self.assertContains(response, 'id="monthly-order-totals"')

    def test_dashboard_loads_chart_scripts(self):
        """Check if scripts needed for the chart are loaded"""
        response = self.client.get(reverse("staff_dashboard"))

        self.assertContains(
            response,
            "https://cdn.jsdelivr.net/npm/chart.js",
        )
        self.assertContains(
            response,
            "dashboard/js/dashboard.js",
        )

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

    def test_dashboard_calculates_days_until_out_of_stock(self):
        """Check if days until out of stock are calculated"""
        category = Category.objects.create(
            category_name="Test Category",
        )
        subcategory = Subcategory.objects.create(
            subcategory_name="Test Subcategory",
            category=category,
        )
        manufacturer = Manufacturer.objects.create(
            manufacturer_name="Test Manufacturer",
        )
        product = Product.objects.create(
            subcategory=subcategory,
            manufacturer=manufacturer,
            product_name="Test Product",
            description="Test product",
            price=Decimal("10.00"),
            in_stock=16,
        )
        order = Order.objects.create(
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

        OrderLineItem.objects.create(
            order=order,
            product=product,
            quantity=8,
        )

        response = self.client.get(reverse("staff_dashboard"))

        stock_estimates = response.context["stock_estimates"]
        dashboard_product = stock_estimates[0]

        # Selling 8 items in 30 days gives an estimated 30 days
        # for the remaining stock of 8 items
        self.assertEqual(
            dashboard_product.days_until_out_of_stock,
            30,
        )

    def test_cancelled_orders_are_excluded_from_stock_estimate(self):
        """Check if cancelled orders are excluded from stock estimation"""
        category = Category.objects.create(
            category_name="Test Category",
        )
        subcategory = Subcategory.objects.create(
            subcategory_name="Test Subcategory",
            category=category,
        )
        manufacturer = Manufacturer.objects.create(
            manufacturer_name="Test Manufacturer",
        )
        product = Product.objects.create(
            subcategory=subcategory,
            manufacturer=manufacturer,
            product_name="Test Product",
            description="Test product",
            price=Decimal("10.00"),
            in_stock=24,
        )
        active_order = Order.objects.create(
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
        cancelled_order = Order.objects.create(
            business_name="Dental Practice Two",
            name="Conor",
            surname="Murphy",
            email="conor@example.com",
            phone_number="+353 86 222 2222",
            address_line_1="2 Main Street",
            town="Dublin",
            postcode="D24 ABC2",
            country="IE",
            status="cancelled",
        )

        OrderLineItem.objects.create(
            order=active_order,
            product=product,
            quantity=8,
        )
        OrderLineItem.objects.create(
            order=cancelled_order,
            product=product,
            quantity=8,
        )

        response = self.client.get(reverse("staff_dashboard"))

        stock_estimates = response.context["stock_estimates"]
        dashboard_product = stock_estimates[0]

        # Both orders reduce the stock from 24 to 8 items
        # Only 8 items from the active order are used in the estimation
        # giving an estimated stock duration of 30 days
        self.assertEqual(
            dashboard_product.days_until_out_of_stock,
            30,
        )

    def test_stock_estimate_is_none_for_product_without_sales(self):
        """Check if stock estimation is unavailable without sales"""
        category = Category.objects.create(
            category_name="Test Category",
        )
        subcategory = Subcategory.objects.create(
            subcategory_name="Test Subcategory",
            category=category,
        )
        manufacturer = Manufacturer.objects.create(
            manufacturer_name="Test Manufacturer",
        )
        Product.objects.create(
            subcategory=subcategory,
            manufacturer=manufacturer,
            product_name="Product Without Sales",
            description="Test product",
            price=Decimal("10.00"),
            in_stock=20,
        )

        response = self.client.get(reverse("staff_dashboard"))

        stock_estimates = response.context["stock_estimates"]
        dashboard_product = stock_estimates[0]

        self.assertIsNone(
            dashboard_product.days_until_out_of_stock
        )

    def test_dashboard_displays_stock_estimates(self):
        """Check if stock estimates are displayed on the dashboard"""
        category = Category.objects.create(
            category_name="Test Category",
        )
        subcategory = Subcategory.objects.create(
            subcategory_name="Test Subcategory",
            category=category,
        )
        manufacturer = Manufacturer.objects.create(
            manufacturer_name="Test Manufacturer",
        )
        Product.objects.create(
            subcategory=subcategory,
            manufacturer=manufacturer,
            product_name="Product Without Sales",
            description="Test product",
            price=Decimal("10.00"),
            in_stock=20,
        )

        response = self.client.get(reverse("staff_dashboard"))

        self.assertContains(
            response,
            "Days Until Out of Stock",
        )
        self.assertContains(
            response,
            "Product Without Sales",
        )
        self.assertContains(
            response,
            "Cannot be calculated",
        )

    def test_products_are_ordered_by_days_until_out_of_stock(self):
        """Check if products expected to run out first are displayed first"""
        category = Category.objects.create(
            category_name="Test Category",
        )
        subcategory = Subcategory.objects.create(
            subcategory_name="Test Subcategory",
            category=category,
        )
        manufacturer = Manufacturer.objects.create(
            manufacturer_name="Test Manufacturer",
        )
        later_product = Product.objects.create(
            subcategory=subcategory,
            manufacturer=manufacturer,
            product_name="Later Product",
            description="Test product",
            price=Decimal("10.00"),
            in_stock=30,
        )
        sooner_product = Product.objects.create(
            subcategory=subcategory,
            manufacturer=manufacturer,
            product_name="Sooner Product",
            description="Test product",
            price=Decimal("10.00"),
            in_stock=16,
        )
        order = Order.objects.create(
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

        OrderLineItem.objects.create(
            order=order,
            product=later_product,
            quantity=6,
        )
        OrderLineItem.objects.create(
            order=order,
            product=sooner_product,
            quantity=8,
        )

        response = self.client.get(reverse("staff_dashboard"))

        stock_estimates = response.context["stock_estimates"]
        product_names = [
            product.product_name
            for product in stock_estimates
        ]

        self.assertEqual(
            product_names,
            ["Sooner Product", "Later Product"],
        )

    def test_product_without_sales_is_displayed_last(self):
        """Check if a product without sales is displayed last"""
        category = Category.objects.create(
            category_name="Test Category",
        )
        subcategory = Subcategory.objects.create(
            subcategory_name="Test Subcategory",
            category=category,
        )
        manufacturer = Manufacturer.objects.create(
            manufacturer_name="Test Manufacturer",
        )
        Product.objects.create(
            subcategory=subcategory,
            manufacturer=manufacturer,
            product_name="Product Without Sales",
            description="Test product",
            price=Decimal("10.00"),
            in_stock=20,
        )
        sold_product = Product.objects.create(
            subcategory=subcategory,
            manufacturer=manufacturer,
            product_name="Sold Product",
            description="Test product",
            price=Decimal("10.00"),
            in_stock=16,
        )
        order = Order.objects.create(
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

        OrderLineItem.objects.create(
            order=order,
            product=sold_product,
            quantity=8,
        )

        response = self.client.get(reverse("staff_dashboard"))

        stock_estimates = response.context["stock_estimates"]
        product_names = [
            product.product_name
            for product in stock_estimates
        ]

        self.assertEqual(
            product_names,
            ["Sold Product", "Product Without Sales"],
        )

    def test_sales_older_than_sales_period_are_excluded(self):
        """Check if sales older than 30 days are excluded"""
        category = Category.objects.create(
            category_name="Test Category",
        )
        subcategory = Subcategory.objects.create(
            subcategory_name="Test Subcategory",
            category=category,
        )
        manufacturer = Manufacturer.objects.create(
            manufacturer_name="Test Manufacturer",
        )
        product = Product.objects.create(
            subcategory=subcategory,
            manufacturer=manufacturer,
            product_name="Test Product",
            description="Test product",
            price=Decimal("10.00"),
            in_stock=16,
        )
        order = Order.objects.create(
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

        OrderLineItem.objects.create(
            order=order,
            product=product,
            quantity=8,
        )

        # Change the order date to make it older than the sales period
        Order.objects.filter(pk=order.pk).update(
            date_of_order=timezone.now() - timedelta(days=31),
        )

        response = self.client.get(reverse("staff_dashboard"))

        stock_estimates = response.context["stock_estimates"]
        dashboard_product = stock_estimates[0]

        self.assertIsNone(
            dashboard_product.days_until_out_of_stock
        )

    def test_stock_estimate_is_rounded_up(self):
        """Check if estimated days are rounded up"""
        category = Category.objects.create(
            category_name="Test Category",
        )
        subcategory = Subcategory.objects.create(
            subcategory_name="Test Subcategory",
            category=category,
        )
        manufacturer = Manufacturer.objects.create(
            manufacturer_name="Test Manufacturer",
        )
        product = Product.objects.create(
            subcategory=subcategory,
            manufacturer=manufacturer,
            product_name="Test Product",
            description="Test product",
            price=Decimal("10.00"),
            in_stock=15,
        )
        order = Order.objects.create(
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

        OrderLineItem.objects.create(
            order=order,
            product=product,
            quantity=7,
        )

        response = self.client.get(reverse("staff_dashboard"))

        stock_estimates = response.context["stock_estimates"]
        dashboard_product = stock_estimates[0]

        # 8 items remain. 7 were sold in 30 days
        # The result is 34.29 days, which is rounded up to 35
        self.assertEqual(
            dashboard_product.days_until_out_of_stock,
            35,
        )

    def test_out_of_stock_product_displays_zero_days(self):
        """Check if an out of stock product displays zero days"""
        category = Category.objects.create(
            category_name="Test Category",
        )
        subcategory = Subcategory.objects.create(
            subcategory_name="Test Subcategory",
            category=category,
        )
        manufacturer = Manufacturer.objects.create(
            manufacturer_name="Test Manufacturer",
        )
        product = Product.objects.create(
            subcategory=subcategory,
            manufacturer=manufacturer,
            product_name="Out of Stock Product",
            description="Test product",
            price=Decimal("10.00"),
            in_stock=8,
        )
        order = Order.objects.create(
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

        OrderLineItem.objects.create(
            order=order,
            product=product,
            quantity=8,
        )

        response = self.client.get(reverse("staff_dashboard"))

        stock_estimates = response.context["stock_estimates"]
        dashboard_product = stock_estimates[0]

        self.assertEqual(
            dashboard_product.days_until_out_of_stock,
            0,
        )
        self.assertContains(
            response,
            "0 days",
        )

    def test_out_of_stock_product_without_sales_displays_zero_days(self):
        """Check if an out of stock product without sales displays zero days"""
        category = Category.objects.create(
            category_name="Test Category",
        )
        subcategory = Subcategory.objects.create(
            subcategory_name="Test Subcategory",
            category=category,
        )
        manufacturer = Manufacturer.objects.create(
            manufacturer_name="Test Manufacturer",
        )
        Product.objects.create(
            subcategory=subcategory,
            manufacturer=manufacturer,
            product_name="Out of Stock Product",
            description="Test product",
            price=Decimal("10.00"),
            in_stock=0,
        )

        response = self.client.get(reverse("staff_dashboard"))

        stock_estimates = response.context["stock_estimates"]
        dashboard_product = stock_estimates[0]

        self.assertEqual(
            dashboard_product.days_until_out_of_stock,
            0,
        )
        self.assertContains(
            response,
            "0 days",
        )
