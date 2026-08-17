from django import forms

from contact_us.validators import validate_phone_number

from .models import Order


class OrderForm(forms.ModelForm):
    phone_number = forms.CharField(
        max_length=20,
        required=True,
        validators=[validate_phone_number],  # apply validator
    )
    postcode = forms.CharField(
        max_length=15,
        required=True,
    )

    class Meta:
        model = Order
        fields = (
            'name', 'surname', 'email', 'phone_number', 'address_line_1',
            'address_line_2', 'town', 'postcode', 'country'
        )

    def __init__(self, *args, **kwargs):
        """
        Add placeholders and classes, remove auto generated labels
        and set autofocus
        """
        super().__init__(*args, **kwargs)
        placeholders = {
            'name': 'First Name',
            'surname': 'Last Name',
            'email': 'Email Address',
            'phone_number': 'Phone Number',
            'address_line_1': 'Address line 1',
            'address_line_2': 'Address line 2',
            'town': 'Town',
            'postcode': 'Eircode / Postcode',
            'country': 'Country',
        }

        self.fields['name'].widget.attrs['autofocus'] = True
        for field in self.fields:
            if self.fields[field].required:
                placeholder = f'{placeholders[field]} *'
            else:
                placeholder = placeholders[field]

            self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].widget.attrs['class'] = 'checkout'
            self.fields[field].label = False


class OrderStatusForm(forms.ModelForm):
    """Form used by staff to update an order status"""

    class Meta:
        model = Order
        fields = ('status',)
