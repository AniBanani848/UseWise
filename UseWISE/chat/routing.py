from django.urls import path

from . import consumers


websocket_urlpatterns = [
    path("ws/chat/<int:friendship_id>/", consumers.ChatConsumer.as_asgi()),
]

