from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Chat, ChatMembership, Message

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ["id", "chat", "sender", "content", "created_at"]
        read_only_fields = ["id", "sender", "created_at", "chat"]


class ChatSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = ["id", "is_group", "name", "created_at", "members", "last_message"]

    def get_members(self, obj):
        users = User.objects.filter(chat_memberships__chat=obj)
        return UserSerializer(users, many=True).data

    def get_last_message(self, obj):
        msg = obj.messages.order_by("-created_at").first()
        if not msg:
            return None
        return MessageSerializer(msg).data


class PrivateChatCreateSerializer(serializers.Serializer):
    other_user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source="other_user"
    )


class GroupChatCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    member_ids = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=User.objects.all()),
        required=False,
        allow_empty=True,
    )

    def validate(self, data):
        if not data.get("name"):
            raise serializers.ValidationError("Group name is required.")
        return data
