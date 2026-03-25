from django.conf import settings
from django.contrib.auth import login
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.core.mail import send_mail
from django.contrib.auth import views as auth_views

from .forms import SignupForm
from .models import User
from .tokens import email_verification_token_generator


def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()

            token = email_verification_token_generator.make_token(user)
            uidb64 = urlsafe_base64_encode(str(user.pk).encode("utf-8"))
            verify_path = reverse("accounts:verify_email", kwargs={"uidb64": uidb64, "token": token})
            verify_url = request.build_absolute_uri(verify_path)

            subject = "UseWISE: потвърдете имейла си"
            message = (
                f"Здравейте!\n\n"
                f"Моля потвърдете имейла си, като отворите линка:\n{verify_url}\n\n"
                f"Ако не сте заявили регистрация, игнорирайте това съобщение."
            )
            from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None) or "no-reply@usewise.local"

            send_mail(subject, message, from_email, [user.email])

            return redirect("accounts:signup_done")
    else:
        form = SignupForm()

    return render(request, "accounts/signup.html", {"form": form})


def signup_done(request):
    return render(request, "accounts/signup_done.html")


def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_object_or_404(User, pk=uid)
    except (TypeError, ValueError, OverflowError):
        user = None

    if user is None:
        return render(request, "accounts/verify_email_invalid.html")

    # If already activated, show success regardless of token validity.
    if user.is_active:
        return render(request, "accounts/verify_email.html", {"user": user})

    if email_verification_token_generator.check_token(user, token):
        user.is_active = True
        user.save(update_fields=["is_active"])
        login(request, user)  # session starts after successful verification
        return render(request, "accounts/verify_email.html", {"user": user})

    return render(request, "accounts/verify_email_invalid.html")


class LoginView(auth_views.LoginView):
    template_name = "accounts/login.html"

