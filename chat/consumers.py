import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Chat, ChatMembership, Message

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket for realtime messages.
    URL: ws://<host>/ws/chat/{chat_id}/
    Auth: Django session (via AuthMiddlewareStack)
    """

    async def connect(self):
        self.chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
        self.room_group_name = f"chat_{self.chat_id}"

        user = self.scope["user"]
        if not user.is_authenticated:
            await self.close()
            return

        is_member = await self._is_member(user.id, self.chat_id)
        if not is_member:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return
        data = json.loads(text_data)
        message = data.get("message", "").strip()
        if not message:
            return

        user = self.scope["user"]
        msg = await self._create_message(user.id, self.chat_id, message)

        event = {
            "type": "chat_message",
            "id": str(msg.id),
            "message": msg.content,
            "sender_id": msg.sender_id,
            "chat_id": str(msg.chat_id),
            "created_at": msg.created_at.isoformat(),
        }

        await self.channel_layer.group_send(self.room_group_name, event)

    async def chat_message(self, event):
        # Send to WebSocket
        await self.send(text_data=json.dumps(event))

    # ---------- DB helpers ----------

    @database_sync_to_async
    def _is_member(self, user_id, chat_id):
        return ChatMembership.objects.filter(chat_id=chat_id, user_id=user_id).exists()

    @database_sync_to_async
    def _create_message(self, user_id, chat_id, content):
        user = User.objects.get(pk=user_id)
        chat = Chat.objects.get(pk=chat_id)
        return Message.objects.create(chat=chat, sender=user, content=content)
