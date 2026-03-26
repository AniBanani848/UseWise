import json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
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
            messages.success(
                request,
                "Регистрацията е успешна. Провери имейла си за потвърждение.",
            )
            return redirect("accounts:signup_done")
    else:
        form = SignupForm()
    return render(request, "accounts/signup.html", {"form": form})


@require_GET
def signup_done(request):
    return render(request, "accounts/signup_done.html")


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
            if not user.is_active:
                messages.error(request, "Потвърди имейла си преди вход.")
                return render(request, "accounts/login.html", {"form": form})
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


# --- JSON API ---


@require_http_methods(["POST"])
def signup_api(request):
    form = SignupForm(request.POST)
    if not form.is_valid():
        return JsonResponse(
            {"ok": False, "message": "Невалидни данни за регистрация.", "errors": form.errors},
            status=400,
        )

    user = form.save()
    _send_verification_email(request, user)

    return JsonResponse(
        {
            "ok": True,
            "message": "Регистрацията е успешна. Провери имейла си за потвърждение.",
            "email": user.email,
        },
        status=201,
    )


@require_POST
def login_api(request):
    email = (request.POST.get("email") or "").strip().lower()
    password = request.POST.get("password") or ""
    user = authenticate(request, email=email, password=password)

    if user is None:
        return JsonResponse({"ok": False, "message": "Невалиден имейл или парола."}, status=400)

    if not user.is_active:
        return JsonResponse({"ok": False, "message": "Потвърди имейла си преди вход."}, status=403)

    login(request, user)
    return JsonResponse({"ok": True, "message": "Успешен вход."})


@require_POST
def logout_api(request):
    logout(request)
    return JsonResponse({"ok": True, "message": "Успешен изход."})


@require_http_methods(["GET", "PATCH"])
def me_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({"ok": False, "message": "Не си логнат."}, status=401)

    user = request.user

    if request.method == "PATCH":
        if request.content_type == "application/json":
            try:
                payload = json.loads(request.body or b"{}")
            except json.JSONDecodeError:
                return JsonResponse({"ok": False, "message": "Невалиден JSON."}, status=400)
        else:
            payload = request.POST

        allowed_fields = {"first_name", "last_name", "country", "city_or_village", "phone"}
        updates = {k: v for k, v in payload.items() if k in allowed_fields}

        if not updates:
            return JsonResponse(
                {"ok": False, "message": "Няма подадени валидни полета за обновяване."},
                status=400,
            )

        errors = {}
        if "phone" in updates:
            raw_phone = str(updates["phone"] or "")
            phone = raw_phone.strip().replace(" ", "").replace("-", "")
            if phone.startswith("+"):
                phone = "+" + "".join(ch for ch in phone[1:] if ch.isdigit())
            else:
                phone = "".join(ch for ch in phone if ch.isdigit())

            if not phone:
                errors["phone"] = "Телефонният номер е задължителен."
            elif User.objects.exclude(pk=user.pk).filter(phone=phone).exists():
                errors["phone"] = "Този телефонен номер вече се използва."
            else:
                updates["phone"] = phone

        for text_field in ("first_name", "last_name", "country", "city_or_village"):
            if text_field in updates:
                value = str(updates[text_field] or "").strip()
                if not value:
                    errors[text_field] = "Полето е задължително."
                else:
                    updates[text_field] = value

        if errors:
            return JsonResponse({"ok": False, "message": "Невалидни данни.", "errors": errors}, status=400)

        for field, value in updates.items():
            setattr(user, field, value)
        user.save(update_fields=list(updates.keys()))

    return JsonResponse(
        {
            "ok": True,
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "country": user.country,
                "city_or_village": user.city_or_village,
                "phone": user.phone,
                "is_active": user.is_active,
            },
        }
    )
