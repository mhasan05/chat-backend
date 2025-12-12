from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ChatViewSet, ChatMessageListCreateView

router = DefaultRouter()
router.register(r"chats", ChatViewSet, basename="chat")

urlpatterns = [
    # RESTful chat endpoints via router
    path("", include(router.urls)),

    # Messages endpoints
    path(
        "chats/<uuid:chat_id>/messages/",
        ChatMessageListCreateView.as_view(),
        name="chat-messages",
    ),
]
