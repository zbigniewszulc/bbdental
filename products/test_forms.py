from django.test import TestCase
from products.forms import ProductForm
from products.models import Manufacturer, Subcategory, Category


class ProductFormTest(TestCase):
    def setUp(self):
        """Create test manufacturer and subcategory"""
        self.category = Category.objects.create(
            category_name="Test Category"
        )
        self.manufacturer = Manufacturer.objects.create(
            manufacturer_name="Test Manufacturer"
        )
        self.subcategory = Subcategory.objects.create(
            subcategory_name="Test Subcategory",
            category=self.category
        )

        self.valid_data = {
            "product_name": "Test Product",
            "description": "A test product description",
            "price": 20.00,
            "in_stock": 10,
            "picture_location": "images/test.jpg",
            "manufacturer": self.manufacturer.id,
            "subcategory": self.subcategory.id
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
            "product_name", "price", "manufacturer", "subcategory"
        ]
        for field in required_fields:
            data = self.valid_data.copy()
            del data[field]

            form = ProductForm(data=data)
            self.assertFalse(form.is_valid(),
                             f"Form should be invalid when missing {field}")
            self.assertIn(field, form.errors)

    def test_product_form_zero_price(self):
        """Test that zero price is not allowed"""
        data = self.valid_data.copy()
        data["price"] = 0.00
        form = ProductForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("price", form.errors)

    def test_product_form_too_long_product_name(self):
        """Test product_name over max_length=50"""
        data = self.valid_data.copy()
        data["product_name"] = "x" * 51
        form = ProductForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("product_name", form.errors)

    def test_product_form_too_long_description(self):
        """Test description over max_length=1000"""
        data = self.valid_data.copy()
        data["description"] = "x" * 1001
        form = ProductForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("description", form.errors)

    def test_product_form_blank_description(self):
        """Test that blank description is invalid"""
        data = self.valid_data.copy()
        data["description"] = ""
        form = ProductForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("description", form.errors)

    def test_product_form_invalid_price_format(self):
        """Test that string value in price field is invalid"""
        data = self.valid_data.copy()
        data["price"] = "twenty"
        form = ProductForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("price", form.errors)

    def test_product_form_invalid_foreign_keys(self):
        """Test that invalid manufacturer or subcategory fails validation"""
        data = self.valid_data.copy()
        data["manufacturer"] = 9999  # nonexistent
        data["subcategory"] = 9999
        form = ProductForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("manufacturer", form.errors)
        self.assertIn("subcategory", form.errors)

    def test_product_form_negative_in_stock(self):
        """Test that negative in_stock is rejected"""
        data = self.valid_data.copy()
        data["in_stock"] = -1
        form = ProductForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("in_stock", form.errors)

    def test_product_form_blank_picture(self):
        """Test that blank picture_location is accepted (optional)"""
        data = self.valid_data.copy()
        data["picture_location"] = ""
        form = ProductForm(data=data)
        self.assertTrue(form.is_valid())
