from django.contrib.auth.tokens import PasswordResetTokenGenerator


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    """
    Token logic for email verification.

    We include user primary key + email + active state so tokens become invalid
    after activation (and if the email changes).
    """

    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{user.email}{timestamp}{user.is_active}"


email_verification_token_generator = EmailVerificationTokenGenerator()

