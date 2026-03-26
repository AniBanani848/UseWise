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
]
