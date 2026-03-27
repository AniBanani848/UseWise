from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from .forms import EmailLoginForm, ProfileEditForm, SignupForm


@require_http_methods(["GET", "POST"])
def signup_html(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Регистрацията е успешна. Добре дошли!")
            return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        form = SignupForm()
    return render(request, "accounts/signup.html", {"form": form})


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
