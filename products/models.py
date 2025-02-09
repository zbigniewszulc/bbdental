from django.db import models

# Create your models here.


class Category(models.Model):
    class Meta:
        verbose_name_plural = 'Categories'

    category_name = models.CharField(max_length=30)
    category_vat = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, default=0
    )
    category_pic_loc = models.ImageField(null=True, blank=True)

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
    manufacturer_name = models.CharField(max_length=50)

    def __str__(self):
        return self.manufacturer_name


class Product(models.Model):
    subcategory_id = models.ForeignKey(
        'Subcategory', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='subcategory_products'
    )
    manufacturer_id = models.ForeignKey(
        'Manufacturer', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='manufacturer_products'
    )
    product_name = models.CharField(max_length=32)
    description = models.TextField(max_length=1000, null=True, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    in_stock = models.IntegerField()
    picture_location = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.product_name
