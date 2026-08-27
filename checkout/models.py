import uuid

from django.conf import settings
from django.db import models
from django.db.models import Sum
from django_countries import Countries
# https://pypi.org/project/django-countries/#custom-forms
from django_countries.fields import CountryField

from products.models import Product
from profiles.models import UserProfile

# Create your models here.


class AllowedCountries(Countries):
    only = [
        "IE", "IT", "FR", "DE", "PL", "CZ", "SK"
    ]


# Core Order and OrderLineItem model structures adapted from
# Code Institute Boutique Ado lesson:
# https://www.youtube.com/watch?v=l1Z9Aau0V08&t=296s
class Order(models.Model):
    # Order fulfilment statuses
    STATUS_CHOICES = [
        ('new', 'New'),
        ('processing', 'Processing'),
        ('dispatched', 'Dispatched'),
        ('cancelled', 'Cancelled'),
    ]
    order_number = models.CharField(max_length=32, null=False, editable=False)
    user_profile = models.ForeignKey(
        UserProfile, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='orders'
    )
    # Customer details
    business_name = models.CharField(max_length=150)
    name = models.CharField(max_length=30, null=False, blank=False)
    surname = models.CharField(max_length=30, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    phone_number = models.CharField(max_length=20, null=False, blank=False)
    # Address section
    address_line_1 = models.CharField(max_length=150, null=False, blank=False)
    address_line_2 = models.CharField(max_length=150, null=True, blank=True)
    town = models.CharField(max_length=50, null=False, blank=False)
    postcode = models.CharField(max_length=15, null=True, blank=True)
    # country uses django-countries package
    country = CountryField(
        blank_label="Select country", countries=AllowedCountries
    )
    # Order details
    date_of_order = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
    )
    delivery_cost = models.DecimalField(
        max_digits=6, decimal_places=2, null=False, default=0.00
    )
    subtotal = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, default=0.00
    )
    grand_total = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, default=0.00
    )
    original_bag = models.TextField(null=True, blank=True)
    stripe_pid = models.CharField(
        max_length=254, null=True, blank=True, unique=True)

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
        # aggregate() adds all line item totals and returns a dictionary
        # The key gets the calculated sum
        # "or 0" uses zero when the order has no line items
        # Sum() defines the calculation, while aggregate() runs it on the data
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
    quantity = models.PositiveIntegerField(null=False, blank=False, default=1)
    line_item_total = models.DecimalField(
        max_digits=6, decimal_places=2,
        null=False, blank=False, editable=False
    )

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the line_item_total
        and update order the total
        """
        unit_price = self.product.get_price_for_quantity(self.quantity)
        self.line_item_total = unit_price * self.quantity

        # Call the save method from the parent class
        super().save(*args, **kwargs)
        self.order.update_total()

    def __str__(self):
        return f'{self.product.product_name} on order {
            self.order.order_number}'
