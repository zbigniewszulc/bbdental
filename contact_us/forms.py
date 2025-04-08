from django import forms
from .validators import validate_phone_number


class ContactForm(forms.Form):
    your_name = forms.CharField(max_length=100, required=True)
    your_email = forms.EmailField(max_length=254, required=True)
    phone_number = forms.CharField(max_length=15, required=False)
    message = forms.CharField(
        widget=forms.Textarea, required=True, min_length=10, max_length=1000
    )

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')

        if phone_number:
            validate_phone_number(phone_number)

        return phone_number
