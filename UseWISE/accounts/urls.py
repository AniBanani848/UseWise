from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    # HTML
    path("signup/", views.signup_html, name="signup"),
    path("signup/done/", views.signup_done, name="signup_done"),
    path("verify-email/<uidb64>/<token>/", views.verify_email, name="verify_email"),
    path("login/", views.login_html, name="login"),
    path("logout/", views.logout_html, name="logout"),
    path("profile/", views.profile_html, name="profile"),
    # JSON API
    path("api/signup/", views.signup_api, name="api_signup"),
    path("api/login/", views.login_api, name="api_login"),
    path("api/logout/", views.logout_api, name="api_logout"),
    path("api/me/", views.me_api, name="api_me"),
]
