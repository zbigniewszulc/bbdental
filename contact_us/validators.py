import re
from django.core.exceptions import ValidationError


def validate_phone_number(phone_number):
    # Regex validation - phone numbers entered with delimiters
    # https://uibakery.io/regex-library/phone-number
    pattern = r'^\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}$'

    # Match the phone number to the pattern
    if not re.match(pattern, phone_number):
        raise ValidationError(
            "Enter a valid phone number."
        )
