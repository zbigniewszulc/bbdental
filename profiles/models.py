from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField
from django_countries import Countries
from django.dispatch import receiver
from django.db.models.signals import post_save
# Create your models here.


class AllowedCountries(Countries):
    only = [
        "IE", "GB", "FR", "DE", "PL", "CZ", "SK"
    ]


class UserProfile(models.Model):
    """
    User profile model for managing default delivery information
    and order history
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    default_phone_number = models.CharField(
        max_length=20, null=True, blank=True
    )
    default_address_line_1 = models.CharField(
        max_length=150, null=True, blank=True
    )
    default_address_line_2 = models.CharField(
        max_length=150, null=True, blank=True
    )
    default_address_line_3 = models.CharField(
        max_length=150, null=True, blank=True
    )
    default_town = models.CharField(
        max_length=50, null=True, blank=True
    )
    default_postcode = models.CharField(
        max_length=15, null=True, blank=True
    )
    default_country = CountryField(
        blank_label="Select country", countries=AllowedCountries
    )

    def __str__(self):
        return self.user.username

    @receiver(post_save, sender=User)
    def create_or_update_user_profile(sender, instance, created, **kwargs):
        """
        Create or update user profile
        """
        if created:
            UserProfile.objects.create(user=instance)
        # For existing users save the profile
        instance.userprofile.save()
