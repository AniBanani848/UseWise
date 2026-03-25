from django import forms
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError

from .models import User


class SignupForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Парола",
        widget=forms.PasswordInput,
        strip=False,
    )
    password2 = forms.CharField(
        label="Потвърди паролата",
        widget=forms.PasswordInput,
        strip=False,
    )

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "country",
            "city_or_village",
            "email",
            "phone",
        )

    def clean_email(self):
        email = self.cleaned_data.get("email") or ""
        return email.strip().lower()

    def clean_phone(self):
        phone = self.cleaned_data.get("phone") or ""
        # Keep digits and leading '+' if provided
        phone = phone.strip().replace(" ", "").replace("-", "")
        if phone.startswith("+"):
            return "+" + "".join(ch for ch in phone[1:] if ch.isdigit())
        return "".join(ch for ch in phone if ch.isdigit())

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match.")

        if password1:
            user = User(email=cleaned_data.get("email") or "temp@example.com")
            password_validation.validate_password(password1, user=user)

        return cleaned_data

    def _create_user(self) -> User:
        user = super().save(commit=False)
        user.is_active = False  # must confirm email first
        user.set_password(self.cleaned_data["password1"])
        user.save()
        return user

    def save(self, commit=True):  # pragma: no cover
        return self._create_user()

