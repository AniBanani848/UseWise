from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.core.mail import send_mail
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .forms import EmailLoginForm, ProfileEditForm, SignupForm
from .models import User
from .tokens import email_verification_token_generator


def _send_verification_email(request, user: User) -> None:
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


# --- HTML (браузър) ---


@require_http_methods(["GET", "POST"])
def signup_html(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            _send_verification_email(request, user)
            return redirect("accounts:signup_done")
    else:
        form = SignupForm()
    return render(request, "accounts/signup.html", {"form": form})


@require_GET
def signup_done(request):
    return render(request, "accounts/signup_done.html")

# 
@require_GET
def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_object_or_404(User, pk=uid)
    except (TypeError, ValueError, OverflowError):
        return render(request, "accounts/verify_email_invalid.html")

    if user.is_active:
        return render(request, "accounts/verify_email_already.html", {"user": user})

    if email_verification_token_generator.check_token(user, token):
        user.is_active = True
        user.save(update_fields=["is_active"])
        login(request, user)
        return render(request, "accounts/verify_email_success.html", {"user": user})

    return render(request, "accounts/verify_email_invalid.html")


@require_http_methods(["GET", "POST"])
def login_html(request):
    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)

    if request.method == "POST":
        form = EmailLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        form = EmailLoginForm(request)

    return render(request, "accounts/login.html", {"form": form})


@require_POST
def logout_html(request):
    logout(request)
    return redirect(settings.LOGOUT_REDIRECT_URL)


@login_required
@require_http_methods(["GET", "POST"])
def profile_html(request):
    if request.method == "POST":
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Профилът е обновен.")
            return redirect("accounts:profile")
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, "accounts/profile.html", {"form": form})
