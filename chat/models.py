import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Chat(models.Model):
    """
    Represents:
    - One-to-one chat (is_group=False, exactly two members)
    - Group chat (is_group=True, many members)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_group = models.BooleanField(default=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name or f"Chat {self.id}"


class ChatMembership(models.Model):
    chat = models.ForeignKey(Chat, related_name="memberships", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="chat_memberships", on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("chat", "user")

    def __str__(self) -> str:
        return f"{self.user} in {self.chat}"


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat = models.ForeignKey(Chat, related_name="messages", on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name="messages", on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"{self.sender} -> {self.chat}: {self.content[:20]}"
