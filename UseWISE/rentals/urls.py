from django.urls import path

from . import views


app_name = "rentals"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("item/<int:item_id>/create/", views.create_rental, name="create"),
    path("<int:rental_id>/approve/", views.approve_rental, name="approve"),
    path("<int:rental_id>/decline/", views.decline_rental, name="decline"),
    path("<int:rental_id>/cancel/", views.cancel_rental, name="cancel"),
]
