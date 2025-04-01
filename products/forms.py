from django import forms
from .models import Product, Subcategory, Manufacturer


class ProductForm(forms.ModelForm):
    """Form for creating and updating products with related fields."""

    manufacturer = forms.ModelChoiceField(
        queryset=Manufacturer.objects.all().order_by('manufacturer_name'),
        required=True,
        label="Manufacturer",
        empty_label="Select Manufacturer",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    subcategory = forms.ModelChoiceField(
        queryset=Subcategory.objects.all().order_by('subcategory_name'),
        required=True,
        label="Subcategory",
        empty_label="Select Subcategory",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Product
        fields = [
            "product_name", "description", "price", "in_stock",
            "picture_location", "manufacturer", "subcategory"
        ]

    def clean_price(self):
        """Price must be positive value and > 0"""
        price = self.cleaned_data.get('price')
        if price < 0:
            raise forms.ValidationError(
                "Price must be a positive value and greater than 0."
            )
        return price

    def clean_in_stock(self):
        """Stock quantity cannot be negative."""
        in_stock = self.cleaned_data.get('in_stock')
        if in_stock < 0:
            raise forms.ValidationError("Stock quantity cannot be negative.")
        return in_stock
