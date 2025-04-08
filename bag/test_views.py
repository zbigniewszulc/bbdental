from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from products.models import Product, Manufacturer, Category, Subcategory


class BagViewsTests(TestCase):
    def setUp(self):
        """Create user and product test"""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="password123")
        self.client.login(username="testuser", password="password123")

        # Create Manufacturer and Subcategory
        manufacturer = Manufacturer.objects.create(
            manufacturer_name="Test Manufacturer")
        category = Category.objects.create(
            category_name="Test Category")
        subcategory = Subcategory.objects.create(
            subcategory_name="Test Subcategory", category=category)

        # Create Product 
        self.product = Product.objects.create(
            product_name="Test Product",
            description="This is a test product",
            price=20.00,
            in_stock=10,
            manufacturer=manufacturer,
            subcategory=subcategory
        )

    def test_view_bag(self):
        """Check if bag is loading"""
        response = self.client.get(reverse("view_bag"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bag/bag.html")

    def test_remove_from_bag(self):
        """Check if can be deleted """
        session = self.client.session
        session["bag"] = {str(self.product.id): 3}
        session.save()

        self.client.post(reverse("update_bag"), {
            "product_id": self.product.id,
            "quantity": 0
        })

        session_bag = self.client.session["bag"]
        self.assertNotIn(str(self.product.id), session_bag)
