import uuid

from django.db import models

from apps.users.models import CustomerUser


class ChatSession(models.Model):
    """
    One chat session belonging to one CustomerUser.

    ``session_id`` is the primary key, and the foreign key targets
    ``CustomerUser.user_id`` (that model's primary key). Each table
    therefore has exactly one identifier, and ``session.user_id`` holds the
    customer's UUID itself.
    """

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        ENDED = "ENDED", "Ended"

    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        CustomerUser,
        related_name="sessions",
        on_delete=models.CASCADE,
    )
    messages = models.JSONField(default=list, blank=True)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.ACTIVE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "chat_sessions"
        ordering = ["-created_at"]

    @property
    def email(self):
        """Sessions no longer duplicate the email; it lives on the user."""
        return self.user.email

    def __str__(self):
        return f"{self.user.email} - {self.session_id}"
