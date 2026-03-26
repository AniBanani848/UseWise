from django.contrib.auth.models import AbstractUser, UserManager as DjangoUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(DjangoUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")

        email = self.normalize_email(email)
        username = extra_fields.pop("username", email)
        return super()._create_user(username, email, password, **extra_fields)

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


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
    objects = UserManager()

    def __str__(self) -> str:
        return self.email

    def save(self, *args, **kwargs):
        # Ensure `username` (required + unique in AbstractUser) doesn't block
        # user creation; we use email as the actual login identifier.
        if not self.username and self.email:
            self.username = self.email
        super().save(*args, **kwargs)

