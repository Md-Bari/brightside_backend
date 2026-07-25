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

    def test_end_session(self):
        create_resp = self.client.post(
            "/api/v1/sessions/", {"email": "customer2@brightside.com"}, format="json"
        )
        session_id = create_resp.data["data"]["session_id"]

        end_resp = self.client.post(
            "/api/v1/sessions/end/", {"session_id": session_id}, format="json"
        )
        self.assertEqual(end_resp.status_code, 200)
        self.assertEqual(end_resp.data["data"]["status"], "ENDED")

    def test_admin_sessions_do_not_require_authentication(self):
        create_resp = self.client.post(
            "/api/v1/sessions/", {"email": "customer3@brightside.com"}, format="json"
        )
        session_id = create_resp.data["data"]["session_id"]
        response = self.client.get(f"/api/v1/admin/sessions/{session_id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.data["data"]["session_id"]), str(session_id))
