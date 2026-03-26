"""
URL configuration for UseWISE project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

from .views import home

urlpatterns = [
    path("", home, name="home"),
    path(
        "signup/",
        RedirectView.as_view(pattern_name="accounts:signup", permanent=False),
        name="signup-redirect",
    ),
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("items/", include("items.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
