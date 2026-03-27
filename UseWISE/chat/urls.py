from django.urls import path

from . import views


app_name = "chat"

urlpatterns = [
    path("", views.contact_list, name="list"),
    path("add/", views.add_contact, name="add_contact"),
    path("start/<int:user_id>/", views.start_direct_chat, name="start_direct"),
    path("request/<int:pk>/accept/", views.accept_contact, name="accept_contact"),
    path("request/<int:pk>/decline/", views.decline_contact, name="decline_contact"),
    path("room/<int:friendship_id>/", views.chat_room, name="room"),
]
