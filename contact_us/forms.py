from django import forms


class ContactForm(forms.Form):
    your_name = forms.CharField(max_length=100, required=True)
    your_email = forms.EmailField(max_length=254, required=True)
    phone_number = forms.CharField(max_length=15, required=False)
    message = forms.CharField(
        widget=forms.Textarea, required=True, min_length=10, max_length=1000
    )
