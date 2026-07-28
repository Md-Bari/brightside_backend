import uuid

from django.test import TestCase
from rest_framework.test import APIClient


class SessionAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_session_returns_session_id_and_user_id(self):
        response = self.client.post(
            "/api/v1/sessions/", {"email": "customer@brightside.com"}, format="json"
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data["success"])
        data = response.data["data"]
        # Both identifiers must be valid UUIDs.
        uuid.UUID(str(data["session_id"]))
        uuid.UUID(str(data["user_id"]))

    def test_auto_end_session_after_inactivity(self):
        from django.utils import timezone
        from datetime import timedelta
        from apps.sessions.models import ChatSession

        create_resp = self.client.post(
            "/api/v1/sessions/", {"email": "customer2@brightside.com"}, format="json"
        )
        session_id = create_resp.data["data"]["session_id"]

        # Simulate 11 minutes of inactivity by manually backdating updated_at
        past_time = timezone.now() - timedelta(minutes=11)
        ChatSession.objects.filter(session_id=session_id).update(updated_at=past_time)

        # Attempting to load/chat in the session should fail with 410
        response = self.client.post(
            "/api/v1/chat/message/",
            {"session_id": session_id, "message": "hello"},
            format="json",
        )
        self.assertEqual(response.status_code, 410)

        # Verify status in database is ENDED
        session = ChatSession.objects.get(session_id=session_id)
        self.assertEqual(session.status, ChatSession.Status.ENDED)
        self.assertIsNotNone(session.ended_at)

    def test_admin_sessions_do_not_require_authentication(self):
        create_resp = self.client.post(
            "/api/v1/sessions/", {"email": "customer3@brightside.com"}, format="json"
        )
        session_id = create_resp.data["data"]["session_id"]
        response = self.client.get(f"/api/v1/admin/sessions/{session_id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.data["data"]["session_id"]), str(session_id))
