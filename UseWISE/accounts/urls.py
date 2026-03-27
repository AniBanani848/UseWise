from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("signup/", views.signup_html, name="signup"),
    path("login/", views.login_html, name="login"),
    path("logout/", views.logout_html, name="logout"),
    path("profile/", views.profile_html, name="profile"),
]
