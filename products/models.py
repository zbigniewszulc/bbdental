from django.db import models
from cloudinary.models import CloudinaryField
# https://studygyaan.com/django/how-to-implement-validators-in-django-models
from django.core.validators import MinValueValidator

# Create your models here.


class Category(models.Model):
    class Meta:
        verbose_name_plural = 'Categories'

    category_name = models.CharField(max_length=30)

    def __str__(self):
        return self.category_name


class Subcategory(models.Model):
    class Meta:
        verbose_name_plural = 'Subcategories'

    subcategory_name = models.CharField(max_length=30)
    category_id = models.ForeignKey(
        'Category',
        null=True, blank=True,
        on_delete=models.SET_NULL,
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
        'Subcategory', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='subcategory_products'
    )
    manufacturer = models.ForeignKey(
        'Manufacturer', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='manufacturer_products'
    )
    product_name = models.CharField(max_length=50)
    description = models.TextField(max_length=1000, null=True)
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]  # Positive DecimalField
    )
    in_stock = models.PositiveIntegerField()
    picture_location = CloudinaryField('image', null=True, blank=True)

    def __str__(self):
        return self.product_name
