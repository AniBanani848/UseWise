import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone

from .models import ChatMessage, Friendship


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.friendship_id = int(self.scope["url_route"]["kwargs"]["friendship_id"])
        self.user = self.scope["user"]

        if self.user.is_anonymous:
            await self.close(code=4401)
            return

        if not await self._user_allowed_in_friendship():
            await self.close(code=4403)
            return

        self.room_group_name = f"chat_{self.friendship_id}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data or "{}")
        except json.JSONDecodeError:
            return

        body = (data.get("message") or "").strip()
        if not body:
            return

        payload = await self._persist_and_build_payload(body[:2000])
        if not payload:
            return

        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "relay_message", "payload": payload},
        )

    async def relay_message(self, event):
        await self.send(text_data=json.dumps(event["payload"]))

    @database_sync_to_async
    def _user_allowed_in_friendship(self):
        try:
            friendship = Friendship.objects.get(
                pk=self.friendship_id,
                status=Friendship.Status.ACCEPTED,
            )
        except Friendship.DoesNotExist:
            return False
        return self.user.pk in (friendship.from_user_id, friendship.to_user_id)

    @database_sync_to_async
    def _persist_and_build_payload(self, body):
        try:
            friendship = Friendship.objects.get(
                pk=self.friendship_id,
                status=Friendship.Status.ACCEPTED,
            )
        except Friendship.DoesNotExist:
            return None

        if self.user.pk not in (friendship.from_user_id, friendship.to_user_id):
            return None

        message = ChatMessage.objects.create(
            friendship=friendship,
            sender=self.user,
            body=body,
        )
        return {
            "type": "message",
            "id": message.pk,
            "body": message.body,
            "sender_id": message.sender_id,
            "username": message.sender.get_full_name() or message.sender.email,
            "created_at": timezone.localtime(message.created_at).isoformat(),
        }

