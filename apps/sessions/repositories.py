"""
Repository layer: all ORM operations for ChatSession.
"""
from django.utils import timezone

from .models import ChatSession


class SessionRepository:
    def create(self, user) -> ChatSession:
        return ChatSession.objects.create(user=user, messages=[])

    def get_by_session_id(self, session_id) -> ChatSession | None:
        return (
            ChatSession.objects.select_related("user")
            .filter(session_id=session_id)
            .first()
        )

    def list_all(self):
        return ChatSession.objects.select_related("user").all()

    def list_for_user(self, user):
        return ChatSession.objects.filter(user=user)

    def save_messages(self, session: ChatSession, messages: list[dict]) -> ChatSession:
        session.messages = messages
        session.save(update_fields=["messages", "updated_at"])
        return session

    def end_session(self, session: ChatSession) -> ChatSession:
        session.status = ChatSession.Status.ENDED
        session.ended_at = timezone.now()
        session.save(update_fields=["status", "ended_at", "updated_at"])
        return session

    def delete(self, session_id) -> bool:
        deleted, _ = ChatSession.objects.filter(session_id=session_id).delete()
        return deleted > 0
