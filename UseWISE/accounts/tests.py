from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode

from .tokens import email_verification_token_generator


User = get_user_model()


class UserManagerTests(TestCase):
    def test_create_user_uses_email_as_username(self):
        user = User.objects.create_user(
            email="manager@example.com",
            password="StrongPass123!",
            first_name="Manager",
            last_name="Test",
            country="Bulgaria",
            city_or_village="Sofia",
            phone="+359888000111",
        )

        self.assertEqual(user.email, "manager@example.com")
        self.assertEqual(user.username, "manager@example.com")
        self.assertTrue(user.check_password("StrongPass123!"))


class SignupFlowTests(TestCase):
    def test_signup_creates_inactive_user_and_sends_verification_email(self):
        response = self.client.post(
            reverse("accounts:signup"),
            {
                "first_name": "Ivan",
                "last_name": "Ivanov",
                "country": "Bulgaria",
                "city_or_village": "Sofia",
                "email": "ivan@example.com",
                "phone": "+359888000333",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )

        user = User.objects.get(email="ivan@example.com")

        self.assertRedirects(response, reverse("accounts:signup_done"))
        self.assertFalse(user.is_active)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(reverse("accounts:verify_email", kwargs={"uidb64": urlsafe_base64_encode(str(user.pk).encode("utf-8")), "token": email_verification_token_generator.make_token(user)}), mail.outbox[0].body)

    def test_verify_email_activates_user_and_logs_them_in(self):
        user = User.objects.create_user(
            email="verify@example.com",
            password="StrongPass123!",
            first_name="Verify",
            last_name="User",
            country="Bulgaria",
            city_or_village="Varna",
            phone="+359888000444",
            is_active=False,
        )

        response = self.client.get(
            reverse(
                "accounts:verify_email",
                kwargs={
                    "uidb64": urlsafe_base64_encode(str(user.pk).encode("utf-8")),
                    "token": email_verification_token_generator.make_token(user),
                },
            )
        )

        user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(user.is_active)
        self.assertEqual(str(self.client.session["_auth_user_id"]), str(user.pk))


class LoginFlowTests(TestCase):
    def setUp(self):
        self.password = "StrongPass123!"
        self.user = User.objects.create_user(
            email="login@example.com",
            password=self.password,
            first_name="Login",
            last_name="Tester",
            country="Bulgaria",
            city_or_village="Plovdiv",
            phone="+359888000222",
        )

    def test_login_page_is_plain_django_form(self):
        response = self.client.get(reverse("accounts:login"))

        self.assertContains(response, "<form", html=False)
        self.assertNotContains(response, "login.js")
        self.assertNotContains(response, "data-login-form")

    def test_html_login_post_authenticates_active_user(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": self.user.email, "password": self.password},
        )

        self.assertRedirects(response, reverse("home"))
        self.assertEqual(str(self.client.session["_auth_user_id"]), str(self.user.pk))

    def test_inactive_user_cannot_log_in(self):
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])

        response = self.client.post(
            reverse("accounts:login"),
            {"username": self.user.email, "password": self.password},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].non_field_errors())
        self.assertNotIn("_auth_user_id", self.client.session)
