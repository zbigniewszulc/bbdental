import uuid
from django.db import models
# https://pypi.org/project/django-countries/#custom-forms
from django_countries.fields import CountryField
from django_countries import Countries
from django.db.models import Sum
from django.conf import settings
from products.models import Product

# Create your models here.


class AllowedCountries(Countries):
    only = [
        "IE", "GB", "FR", "DE", "PL", "CZ", "SK"
    ]


class Order(models.Model):
    order_number = models.CharField(max_length=32, null=False, editable=False)
    # Customer details
    name = models.CharField(max_length=30, null=False, blank=False)
    surname = models.CharField(max_length=30, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    phone_number = models.CharField(max_length=20, null=False, blank=False)
    # Address section
    address_line_1 = models.CharField(max_length=150, null=False, blank=False)
    address_line_2 = models.CharField(max_length=150, null=True, blank=True)
    address_line_3 = models.CharField(max_length=150, null=True, blank=True)
    town = models.CharField(max_length=50, null=False, blank=False)
    postcode = models.CharField(max_length=15, null=True, blank=True)
    # country uses django-countries package
    country = CountryField(blank_label="Select country",
                           countries=AllowedCountries)
    # Order details
    date_of_order = models.DateTimeField(auto_now_add=True)
    delivery_cost = models.DecimalField(
        max_digits=6, decimal_places=2, null=False, default=0.00)
    subtotal = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, default=0.00)
    grand_total = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, default=0.00)

    def _generate_order_number(self):
        """
        Generate random 32 characters string and unique order number
        """
        return uuid.uuid4().hex.upper()

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the order number
        if not already set
        """
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def update_total(self):
        """
        Update grand total each time a line item is added
        along with delivery cost
        """
        self.subtotal = self.line_items.aggregate(
            Sum('line_item_total'))['line_item_total__sum'] or 0

        if self.subtotal < settings.FREE_DELIVERY_THRESHOLD:
            self.delivery_cost = settings.STANDARD_DELIVERY_COST
        else:
            self.delivery_cost = 0
        self.grand_total = self.subtotal + self.delivery_cost
        self.save()

    def __str__(self):
        return self.order_number


class OrderLineItem(models.Model):
    order = models.ForeignKey(
        Order, null=False, blank=False, on_delete=models.CASCADE,
        related_name='line_items'
    )
    product = models.ForeignKey(
        Product, null=False, blank=False, on_delete=models.CASCADE
    )
    quantity = models.IntegerField(null=False, blank=False, default=1)
    line_item_total = models.DecimalField(
        max_digits=6, decimal_places=2,
        null=False, blank=False, editable=False
    )

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the line_item_total
        and update order the total
        """
        self.line_item_total = self.product.price * self.quantity
        super().save(*args, **kwargs)
        self.order.update_total()

    def __str__(self):
        return f'{self.product.product_name} on order {
            self.order.order_number}'
