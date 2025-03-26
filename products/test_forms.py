from django.test import TestCase
from products.forms import ProductForm
from products.models import Manufacturer, Subcategory


class ProductFormTest(TestCase):
    def setUp(self):
        """Create test manufacturer and subcategory"""
        self.manufacturer = Manufacturer.objects.create(
            manufacturer_name="Test Manufacturer")
        self.subcategory = Subcategory.objects.create(
            subcategory_name="Test Subcategory")

        self.valid_data = {
            "product_name": "Test Product",
            "description": "A test product description",
            "price": 20.00,
            "in_stock": 10,
            "picture_location": "images/test.jpg",
            "manufacturer": self.manufacturer,
            "subcategory_id": self.subcategory
        }

    def test_product_form_valid(self):
        """Test if form is valid with correct data"""
        form = ProductForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_product_form_negative_price(self):
        """Test that negative price raises validation error"""
        data = self.valid_data.copy()
        data["price"] = -5.00

        form = ProductForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("price", form.errors)
        self.assertEqual(
            form.errors["price"][0],
            "Price must be a positive value and greater than 0."
        )

    def test_product_form_missing_required_fields(self):
        """Test that missing required fields cause form errors"""
        required_fields = [
            "product_name", "price", "manufacturer", "subcategory_id"
        ]
        for field in required_fields:
            data = self.valid_data.copy()
            del data[field]

            form = ProductForm(data=data)
            self.assertFalse(form.is_valid(),
                             f"Form should be invalid when missing {field}")
            self.assertIn(field, form.errors)
