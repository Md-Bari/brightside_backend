"""
Business logic for session lifecycle: creation, message persistence, ending.
"""
import logging

from apps.common.exceptions import NotFoundServiceError, ServiceError
from apps.users.services import UserService

from .models import ChatSession
from .repositories import SessionRepository

logger = logging.getLogger("brightside")


class SessionService:
    def __init__(self, repository: SessionRepository | None = None, user_service: UserService | None = None):
        self.repository = repository or SessionRepository()
        self.user_service = user_service or UserService()

    def create_session(self, email: str, name: str = "") -> ChatSession:
        from apps.campaigns.models import Campaign
        from apps.campaigns.serializers import CampaignSerializer

        user = self.user_service.get_or_create_user(email, name=name)
        session = self.repository.create(user=user)

        # Get active campaigns
        active_campaigns = Campaign.objects.filter(is_active=True)
        campaigns_data = CampaignSerializer(active_campaigns, many=True).data

        # Build welcome message with campaign info
        greeting = (
            f"Hello {name or 'there'}! Welcome to Brightside Car Wash. "
            f"How can I help you today?"
        )

        # Store welcome message and campaigns info in JSONB messages
        messages = list(session.messages or [])
        messages.append({"role": "assistant", "content": greeting})
        if campaigns_data:
            messages.append({
                "role": "system",
                "content": "Active campaigns information",
                "campaigns": campaigns_data
            })
        session = self.repository.save_messages(session, messages)

        logger.info("Created session %s for %s", session.session_id, user.email)
        return session

    def get_active_session(self, session_id) -> ChatSession:
        session = self.repository.get_by_session_id(session_id)
        if not session:
            raise NotFoundServiceError("Session not found.")
        if session.status == ChatSession.Status.ENDED:
            raise ServiceError("This session has already ended.", status_code=410)
        return session

    def get_session(self, session_id) -> ChatSession:
        session = self.repository.get_by_session_id(session_id)
        if not session:
            raise NotFoundServiceError("Session not found.")
        return session

    def append_message(self, session: ChatSession, role: str, content: str) -> ChatSession:
        messages = list(session.messages or [])
        messages.append({"role": role, "content": content})
        return self.repository.save_messages(session, messages)

    def end_session(self, session_id) -> ChatSession:
        session = self.get_session(session_id)
        if session.status == ChatSession.Status.ENDED:
            return session
        return self.repository.end_session(session)

    # --- Admin operations ---
    def list_all_sessions(self):
        return self.repository.list_all()

    def list_sessions_for_user(self, user):
        return self.repository.list_for_user(user)

    def delete_session(self, session_id) -> None:
        if not self.repository.delete(session_id):
            raise NotFoundServiceError("Session not found.")
