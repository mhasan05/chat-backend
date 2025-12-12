from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("<uuid:chat_id>/", consumers.ChatConsumer.as_asgi(), name="ws-chat"),
]
