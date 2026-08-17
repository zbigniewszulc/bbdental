from django import forms

from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user',)

    def __init__(self, *args, **kwargs):
        """
        Add placeholders and classes, remove auto generated labels
        and set autofocus
        """
        super().__init__(*args, **kwargs)
        placeholders = {
            'business_name': 'Business name',
            'default_phone_number': 'Phone Number',
            'default_address_line_1': 'Address line 1',
            'default_address_line_2': 'Address line 2',
            'default_town': 'Town',
            'default_postcode': 'Postcode',
            'default_country': 'Country',
        }

        self.fields["business_name"].required = True
        self.fields['default_phone_number'].widget.attrs['autofocus'] = True
        for field in self.fields:
            if self.fields[field].required:
                placeholder = f'{placeholders[field]} *'
            else:
                placeholder = placeholders[field]

            self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].widget.attrs['class'] = 'profile-form'
            self.fields[field].label = False


class BusinessNameSignupForm(forms.Form):
    business_name = forms.CharField(
        max_length=150,
        label="Business name",
    )

    def signup(self, request, user):
        """Save the business name to the user's profile"""
        # The profile is created by the post_save signal
        # after the user is saved
        user.userprofile.business_name = self.cleaned_data["business_name"]
        user.userprofile.save()
