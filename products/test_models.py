from django.test import TestCase
from .models import Category, Subcategory, Manufacturer, Product
from django.core.exceptions import ValidationError
from decimal import Decimal


class CategoryModelTest(TestCase):
    def test_category_str_method(self):
        """Test the __str__ method of the Category model."""
        category = Category.objects.create(category_name="Dental Materials")
        self.assertEqual(str(category), "Dental Materials")

    def test_category_unique_name(self):
        """Test that a duplicate category name raises a ValidationError."""
        Category.objects.create(category_name="Dental Materials")
        with self.assertRaises(ValidationError):
            category = Category(category_name="Dental Materials")
            category.full_clean()

    def test_category_empty_name(self):
        """Test that an empty category name raises a ValidationError."""
        category = Category(category_name="")
        with self.assertRaises(ValidationError):
            category.full_clean()

    def test_category_name_length(self):
        """Test that the category name exceeds the maximum length."""
        long_name = "A" * 31  # category_name can be max 30 characters
        category = Category(category_name=long_name)
        with self.assertRaises(ValidationError):
            category.full_clean()


class SubcategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            category_name="Dental Materials")

    def test_subcategory_str_method(self):
        """Test the __str__ method of the Subcategory model."""
        subcategory = Subcategory.objects.create(
            subcategory_name="Endodontic Materials", category=self.category)
        self.assertEqual(str(subcategory), "Endodontic Materials")

    def test_subcategory_unique_name(self):
        """Test that a duplicate subcategory name raises a ValidationError."""
        Subcategory.objects.create(
            subcategory_name="Endodontic Materials", category=self.category)
        with self.assertRaises(ValidationError):
            subcategory = Subcategory(
                subcategory_name="Endodontic Materials", category=self.category
            )
            subcategory.full_clean()

    def test_subcategory_category_relation(self):
        """Test the ForeignKey relation between Subcategory and Category."""
        subcategory = Subcategory.objects.create(
            subcategory_name="Endodontic Materials", category=self.category)
        self.assertEqual(subcategory.category, self.category)

    def test_subcategory_empty_name(self):
        """Test that an empty subcategory name raises a ValidationError."""
        subcategory = Subcategory(subcategory_name="", category=self.category)
        with self.assertRaises(ValidationError):
            subcategory.full_clean()

    def test_subcategory_name_length(self):
        """Test that the subcategory name exceeds the maximum length."""
        long_name = "A" * 31  # subcategory_name can be max 30 characters
        subcategory = Subcategory(
            subcategory_name=long_name, category=self.category)
        with self.assertRaises(ValidationError):
            subcategory.full_clean()


class ManufacturerModelTest(TestCase):
    def test_manufacturer_str_method(self):
        """Test the __str__ method of the Manufacturer model."""
        manufacturer = Manufacturer.objects.create(manufacturer_name="Dentaco")
        self.assertEqual(str(manufacturer), "Dentaco")

    def test_manufacturer_unique_name(self):
        """Test that a duplicate manufacturer name raises a ValidationError."""
        Manufacturer.objects.create(manufacturer_name="Dentaco")
        with self.assertRaises(ValidationError):
            manufacturer = Manufacturer(manufacturer_name="Dentaco")
            manufacturer.full_clean()

    def test_manufacturer_empty_name(self):
        """Test that an empty manufacturer name raises a ValidationError."""
        manufacturer = Manufacturer(manufacturer_name="")
        with self.assertRaises(ValidationError):
            manufacturer.full_clean()

    def test_manufacturer_name_length(self):
        """Test that the manufacturer name exceeds the maximum length."""
        long_name = "A" * 51  # manufacturer_name can be max 50 characters
        manufacturer = Manufacturer(manufacturer_name=long_name)
        with self.assertRaises(ValidationError):
            manufacturer.full_clean()


class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            category_name="Dental Materials")
        self.subcategory = Subcategory.objects.create(
            subcategory_name="Endodontic Materials", category=self.category)
        self.manufacturer = Manufacturer.objects.create(
            manufacturer_name="Dentaco")

    def test_product_str_method(self):
        """Test the __str__ method of the Product model."""
        product = Product.objects.create(
            product_name="Gutta-percha",
            description="A material used in root canal treatments.",
            price=Decimal("29.99"),
            in_stock=150,
            subcategory=self.subcategory,
            manufacturer=self.manufacturer
        )
        self.assertEqual(str(product), "Gutta-percha")

    def test_product_price_validation(self):
        """Test that a negative product price raises a ValidationError."""
        with self.assertRaises(ValidationError):
            product = Product(
                product_name="Invalid Gutta-percha",
                description="This product has a negative price",
                price=Decimal("-1.00"),
                in_stock=150,
                subcategory=self.subcategory,
                manufacturer=self.manufacturer
            )
            product.full_clean()

    def test_product_in_stock(self):
        """Test that the 'in_stock' field is correctly set."""
        product = Product.objects.create(
            product_name="Gutta-percha",
            description="A material used in root canal treatments.",
            price=Decimal("29.99"),
            in_stock=150,
            subcategory=self.subcategory,
            manufacturer=self.manufacturer
        )
        self.assertEqual(product.in_stock, 150)

    def test_product_picture_location(self):
        """Test that 'picture_location' field is nullable and can be None"""
        product = Product.objects.create(
            product_name="Gutta-percha",
            description="A material used in root canal treatments.",
            price=Decimal("29.99"),
            in_stock=150,
            subcategory=self.subcategory,
            manufacturer=self.manufacturer,
            picture_location=None
        )
        self.assertIsNone(product.picture_location)

    def test_product_picture_location_not_null(self):
        """Test the 'picture_location' field can be set to a non-null value."""
        product = Product.objects.create(
            product_name="Gutta-percha",
            description="A material used in root canal treatments.",
            price=Decimal("29.99"),
            in_stock=150,
            subcategory=self.subcategory,
            manufacturer=self.manufacturer,
            picture_location="sample_path.jpg"
        )
        self.assertEqual(product.picture_location, "sample_path.jpg")

    def test_product_in_stock_negative(self):
        """Test that a negative value for in_stock raises a ValidationError."""
        with self.assertRaises(ValidationError):
            product = Product(
                product_name="Gutta-percha",
                description="A material used in root canal treatments.",
                price=Decimal("29.99"),
                in_stock=-10,  
                subcategory=self.subcategory,
                manufacturer=self.manufacturer
            )
            product.full_clean()

    def test_product_without_manufacturer(self):
        """Test that a product cannot be created without a manufacturer."""
        product = Product(
            product_name="Gutta-percha",
            description="A material used in root canal treatments.",
            price=Decimal("29.99"),
            in_stock=150,
            subcategory=self.subcategory,
            manufacturer=None  
        )
        with self.assertRaises(ValidationError):
            product.full_clean()

    def test_product_price_edge_case(self):
        """Test that the product price is valid at the edge case of 0.01."""
        product = Product.objects.create(
            product_name="Gutta-percha",
            description="A material used in root canal treatments.",
            price=Decimal("0.01"),  # Minimum allowed price
            in_stock=150,
            subcategory=self.subcategory,
            manufacturer=self.manufacturer
        )
        self.assertEqual(product.price, Decimal("0.01"))

    def test_product_stock_zero(self):
        """Test that a product with zero stock is allowed
        but should be treated as out of stock."""
        product = Product.objects.create(
            product_name="Gutta-percha",
            description="A material used in root canal treatments.",
            price=Decimal("29.99"),
            in_stock=0,
            subcategory=self.subcategory,
            manufacturer=self.manufacturer
        )
        self.assertEqual(product.in_stock, 0)
