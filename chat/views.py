from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Chat, ChatMembership, Message
from .serializers import (
    ChatSerializer,
    PrivateChatCreateSerializer,
    GroupChatCreateSerializer,
    MessageSerializer,
)
from .permissions import IsChatMember

User = get_user_model()


class ChatViewSet(viewsets.ModelViewSet):
    """
    Chat list / create / retrieve.
    - GET /api/chats/ -> user's chats
    - GET /api/chats/{id}/ -> chat detail (must be member)
    - POST /api/chats/private/ -> create/find 1-1 chat
    - POST /api/chats/group/ -> create group chat
    """
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only chats current user is part of
        return Chat.objects.filter(memberships__user=self.request.user).distinct()

    def retrieve(self, request, *args, **kwargs):
        # ensure membership via get_queryset()
        instance = self.get_queryset().get(pk=kwargs["pk"])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="private")
    def create_private_chat(self, request):
        """
        Create or fetch a 1-1 chat between current user and other_user_id.
        """
        serializer = PrivateChatCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        other_user = serializer.validated_data["other_user"]

        if other_user == request.user:
            return Response(
                {"detail": "Cannot create private chat with yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # find existing private chat
        existing = (
            Chat.objects.filter(is_group=False)
            .filter(memberships__user=request.user)
            .filter(memberships__user=other_user)
            .distinct()
            .first()
        )
        if existing:
            return Response(ChatSerializer(existing).data, status=status.HTTP_200_OK)

        with transaction.atomic():
            chat = Chat.objects.create(is_group=False)
            ChatMembership.objects.create(chat=chat, user=request.user)
            ChatMembership.objects.create(chat=chat, user=other_user)

        return Response(ChatSerializer(chat).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="group")
    def create_group_chat(self, request):
        """
        Create a group chat with a name and optional member_ids.
        The current user is always added as a member.
        """
        serializer = GroupChatCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        name = serializer.validated_data["name"]
        members = serializer.validated_data.get("member_ids", [])

        with transaction.atomic():
            chat = Chat.objects.create(is_group=True, name=name)
            ChatMembership.objects.create(chat=chat, user=request.user)
            for user in members:
                if user != request.user:
                    ChatMembership.objects.get_or_create(chat=chat, user=user)

        return Response(ChatSerializer(chat).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="add-member")
    def add_member(self, request, pk=None):
        """
        Add a user to a group chat.
        Payload: { "user_id": <int> }
        """
        chat = self.get_queryset().get(pk=pk)
        if not chat.is_group:
            return Response(
                {"detail": "Cannot add members to a private chat."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_id = request.data.get("user_id")
        if not user_id:
            return Response(
                {"detail": "user_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        ChatMembership.objects.get_or_create(chat=chat, user=user)
        return Response(ChatSerializer(chat).data)

    @action(detail=True, methods=["post"], url_path="remove-member")
    def remove_member(self, request, pk=None):
        """
        Remove a user from a group chat.
        Payload: { "user_id": <int> }
        """
        chat = self.get_queryset().get(pk=pk)
        if not chat.is_group:
            return Response(
                {"detail": "Cannot remove members from a private chat."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_id = request.data.get("user_id")
        if not user_id:
            return Response(
                {"detail": "user_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ChatMembership.objects.filter(chat=chat, user_id=user_id).delete()
        return Response(ChatSerializer(chat).data)


class ChatMessageListCreateView(generics.ListCreateAPIView):
    """
    List and create messages in a given chat.
    - GET /api/chats/{chat_id}/messages/
    - POST /api/chats/{chat_id}/messages/
    """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsChatMember]

    def get_queryset(self):
        chat_id = self.kwargs["chat_id"]
        # membership already enforced by permission
        return Message.objects.filter(chat_id=chat_id).select_related("sender")

    def perform_create(self, serializer):
        chat_id = self.kwargs["chat_id"]
        serializer.save(chat_id=chat_id, sender=self.request.user)
