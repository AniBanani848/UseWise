from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom user model:
    - login with email
    - unique phone number
    - extra profile fields for location
    """

    email = models.EmailField(_("имейл"), unique=True)
    phone = models.CharField(_("телефонен номер"), max_length=20, unique=True)

    country = models.CharField(_("държава"), max_length=100)
    city_or_village = models.CharField(_("град/село"), max_length=100)

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"

    REQUIRED_FIELDS = ["first_name", "last_name", "phone", "country", "city_or_village"]

    def __str__(self) -> str:
        return self.email

    def save(self, *args, **kwargs):
        # Ensure `username` (required + unique in AbstractUser) doesn't block
        # user creation; we use email as the actual login identifier.
        if not self.username and self.email:
            self.username = self.email
        super().save(*args, **kwargs)

