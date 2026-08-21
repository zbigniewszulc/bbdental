from cloudinary.models import CloudinaryField
# https://studygyaan.com/django/how-to-implement-validators-in-django-models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

# Create your models here.


class Category(models.Model):
    class Meta:
        verbose_name_plural = 'Categories'

    category_name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.category_name


class Subcategory(models.Model):
    class Meta:
        verbose_name_plural = 'Subcategories'

    subcategory_name = models.CharField(max_length=30, unique=True)
    category = models.ForeignKey(
        'Category',
        on_delete=models.PROTECT,
        related_name='subcategories'
    )

    def __str__(self):
        return self.subcategory_name


class Manufacturer(models.Model):
    manufacturer_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.manufacturer_name


class Product(models.Model):
    subcategory = models.ForeignKey(
        'Subcategory',
        on_delete=models.PROTECT,
        related_name='subcategory_products'
    )
    manufacturer = models.ForeignKey(
        'Manufacturer',
        on_delete=models.PROTECT,
        related_name='manufacturer_products'
    )
    product_name = models.CharField(max_length=50)
    description = models.TextField(max_length=1000)
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]  # Positive DecimalField
    )
    bulk_quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(2)],
        null=True,
        blank=True,
    )
    bulk_price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        null=True,
        blank=True,
    )
    in_stock = models.PositiveIntegerField()
    picture_location = CloudinaryField('image', null=True, blank=True)

    def __str__(self):
        return self.product_name

    def clean(self):
        """Check if bulk price is lower than regular price"""
        if self.bulk_quantity is not None and self.bulk_price is None:
            raise ValidationError({
                'bulk_price': (
                    'Bulk price is required when bulk quantity is provided.'
                )
            })

        if self.bulk_price is not None and self.bulk_quantity is None:
            raise ValidationError({
                'bulk_quantity': (
                    'Bulk quantity is required when bulk price is provided.'
                )
            })

        if (
            # Compare the prices only when both values are provided
            self.price is not None
            and self.bulk_price is not None
            and self.bulk_price >= self.price
        ):
            # Assign the validation error to the bulk_price field
            raise ValidationError({
                'bulk_price': (
                    'Bulk price must be lower than regular price.'
                )
            })

    def get_price_for_quantity(self, quantity):
        """Return the correct product price for the selected quantity"""
        if (
            self.bulk_quantity
            and self.bulk_price
            and quantity >= self.bulk_quantity
        ):
            return self.bulk_price

        return self.price
