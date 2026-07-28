from django.test import TestCase
from rest_framework.test import APIClient

from apps.sessions.models import ChatSession
from apps.users.models import CustomerUser


class CustomerUserTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_creates_user_with_name_and_user_id(self):
        response = self.client.post(
            "/api/v1/sessions/",
            {"email": "testuser@brightside.com", "name": "John Doe"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)

        user = CustomerUser.objects.get(email="testuser@brightside.com")
        self.assertEqual(user.name, "John Doe")
        self.assertIsNotNone(user.user_id)

    def test_creates_session_updates_name_if_blank(self):
        # Create user without name first
        user = CustomerUser.objects.create(email="testuser@brightside.com", name="")

        response = self.client.post(
            "/api/v1/sessions/",
            {"email": "testuser@brightside.com", "name": "John Doe"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)

        user.refresh_from_db()
        self.assertEqual(user.name, "John Doe")

    def test_admin_list_users(self):
        user = CustomerUser.objects.create(email="user1@example.com", name="User One")

        response = self.client.get("/api/v1/admin/users/")
        self.assertEqual(response.status_code, 200)

        data = response.data["data"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["email"], "user1@example.com")
        self.assertEqual(data[0]["name"], "User One")
        self.assertEqual(str(data[0]["user_id"]), str(user.user_id))

    def test_admin_dashboard_pipeline(self):
        """user list -> that user's sessions -> that session's chats."""
        user = CustomerUser.objects.create(email="pipeline@example.com", name="Pipeline")
        session = ChatSession.objects.create(
            user=user,
            messages=[
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"},
            ],
        )

        # Level 1: every user_id
        users = self.client.get("/api/v1/admin/users/").data["data"]
        listed = [u for u in users if str(u["user_id"]) == str(user.user_id)]
        self.assertEqual(len(listed), 1)

        # Level 2: click a user_id -> that user's session_ids
        level2 = self.client.get(f"/api/v1/admin/users/{user.user_id}/sessions/")
        self.assertEqual(level2.status_code, 200)
        body = level2.data["data"]
        self.assertEqual(str(body["user_id"]), str(user.user_id))
        self.assertEqual(len(body["sessions"]), 1)
        self.assertEqual(str(body["sessions"][0]["session_id"]), str(session.session_id))
        self.assertEqual(body["sessions"][0]["message_count"], 2)

        # Level 3: click a session_id -> the chats
        level3 = self.client.get(f"/api/v1/admin/sessions/{session.session_id}/")
        self.assertEqual(level3.status_code, 200)
        chats = level3.data["data"]["messages"]
        self.assertEqual(len(chats), 2)
        self.assertEqual(chats[0]["content"], "Hello")
        self.assertEqual(chats[1]["content"], "Hi there!")

    def test_admin_user_sessions_list(self):
        user = CustomerUser.objects.create(email="user2@example.com", name="User Two")
        session1 = ChatSession.objects.create(user=user)
        session2 = ChatSession.objects.create(user=user)

        response = self.client.get(f"/api/v1/admin/users/{user.user_id}/sessions/")
        self.assertEqual(response.status_code, 200)

        sessions = response.data["data"]["sessions"]
        self.assertEqual(len(sessions), 2)
        session_ids = [str(s["session_id"]) for s in sessions]
        self.assertIn(str(session1.session_id), session_ids)
        self.assertIn(str(session2.session_id), session_ids)

    def test_human_escalation_detection_and_reset(self):
        user = CustomerUser.objects.create(email="escalate@example.com", name="Escalate User")
        session = ChatSession.objects.create(user=user)
        self.assertFalse(user.human_escalation_required)

        from unittest.mock import patch
        with patch("apps.chatbot.services.generate_chat_completion") as mock_completion:
            mock_completion.return_value = "[HUMAN_ESCALATION] I cannot answer. Our staff will communicate with you very soon."

            response = self.client.post(
                "/api/v1/chat/message/",
                {"session_id": str(session.session_id), "message": "Trigger escalation please"},
                format="json",
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.data["data"]["answer"],
                "I cannot answer. Our staff will communicate with you very soon."
            )

        user.refresh_from_db()
        self.assertTrue(user.human_escalation_required)

        view_resp = self.client.get(f"/api/v1/admin/users/{user.user_id}/sessions/")
        self.assertEqual(view_resp.status_code, 200)

        user.refresh_from_db()
        self.assertFalse(user.human_escalation_required)

    def test_human_escalation_detection_via_message_content(self):
        user = CustomerUser.objects.create(email="escalate_content@example.com", name="Escalate Content User")
        session = ChatSession.objects.create(user=user)
        self.assertFalse(user.human_escalation_required)

        from unittest.mock import patch
        with patch("apps.chatbot.services.generate_chat_completion") as mock_completion:
            mock_completion.return_value = "I am unable to assist with this query. Our staff will communicate with you very soon."

            response = self.client.post(
                "/api/v1/chat/message/",
                {"session_id": str(session.session_id), "message": "Trigger escalation please"},
                format="json",
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.data["data"]["answer"],
                "I am unable to assist with this query. Our staff will communicate with you very soon."
            )

        user.refresh_from_db()
        self.assertTrue(user.human_escalation_required)

    def test_admin_list_users_pagination(self):
        # Create 5 users
        # Users Meta ordering is -created_at, so users created later appear first
        u1 = CustomerUser.objects.create(email="user1@example.com", name="User One")
        u2 = CustomerUser.objects.create(email="user2@example.com", name="User Two")
        u3 = CustomerUser.objects.create(email="user3@example.com", name="User Three")

        # Get first page with size 2
        response = self.client.get("/api/v1/admin/users/", {"page_size": 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["data"]), 2)
        
        # Checking that ordering is descending by created_at
        self.assertEqual(response.data["data"][0]["email"], "user3@example.com")
        self.assertEqual(response.data["data"][1]["email"], "user2@example.com")
        
        self.assertIn("meta", response.data)
        self.assertIsNotNone(response.data["meta"]["next"])
        self.assertIsNone(response.data["meta"]["previous"])
        
        # Get second page using the next cursor
        next_url = response.data["meta"]["next"]
        # Extract query parameters or query the full url (APIClient handles full URLs pointing to testserver)
        response_page2 = self.client.get(next_url)
        self.assertEqual(response_page2.status_code, 200)
        self.assertEqual(len(response_page2.data["data"]), 1)
        self.assertEqual(response_page2.data["data"][0]["email"], "user1@example.com")
        self.assertIsNone(response_page2.data["meta"]["next"])
        self.assertIsNotNone(response_page2.data["meta"]["previous"])

    def test_admin_list_users_search(self):
        CustomerUser.objects.create(email="alice@example.com", name="Alice Smith")
        CustomerUser.objects.create(email="bob@example.com", name="Bob Jones")
        CustomerUser.objects.create(email="charlie@example.com", name="Charlie Brown")

        # Search for 'alice' by name
        res = self.client.get("/api/v1/admin/users/", {"search": "alice"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data["data"]), 1)
        self.assertEqual(res.data["data"][0]["name"], "Alice Smith")

        # Search for 'brown' by name (case-insensitive)
        res = self.client.get("/api/v1/admin/users/", {"search": "BROWN"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data["data"]), 1)
        self.assertEqual(res.data["data"][0]["name"], "Charlie Brown")

        # Search for 'bob' by email
        res = self.client.get("/api/v1/admin/users/", {"search": "bob@example.com"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data["data"]), 1)
        self.assertEqual(res.data["data"][0]["email"], "bob@example.com")

        # Search using single 'search' query param
        res = self.client.get("/api/v1/admin/users/", {"search": "jones"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data["data"]), 1)
        self.assertEqual(res.data["data"][0]["name"], "Bob Jones")

        # Search term with no match
        res = self.client.get("/api/v1/admin/users/", {"search": "xyz"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data["data"]), 0)

    def test_admin_list_users_latest_chat_ordering(self):
        # Create three users
        u1 = CustomerUser.objects.create(email="user1@example.com", name="User One")
        u2 = CustomerUser.objects.create(email="user2@example.com", name="User Two")
        u3 = CustomerUser.objects.create(email="user3@example.com", name="User Three")

        # Initially, with no chat sessions, they should be sorted by created_at descending: u3, u2, u1.
        res = self.client.get("/api/v1/admin/users/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["data"][0]["email"], "user3@example.com")
        self.assertEqual(res.data["data"][1]["email"], "user2@example.com")
        self.assertEqual(res.data["data"][2]["email"], "user1@example.com")

        # Now, create a chat session for u2 (user2@example.com)
        ChatSession.objects.create(user=u2)
        
        # Call user list, u2 should be first!
        res = self.client.get("/api/v1/admin/users/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["data"][0]["email"], "user2@example.com")
        self.assertEqual(res.data["data"][1]["email"], "user3@example.com")
        self.assertEqual(res.data["data"][2]["email"], "user1@example.com")

        # Now create a chat session for u1 (user1@example.com)
        ChatSession.objects.create(user=u1)
        
        # Now u1 should be first! u2 second, u3 third.
        res = self.client.get("/api/v1/admin/users/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["data"][0]["email"], "user1@example.com")
        self.assertEqual(res.data["data"][1]["email"], "user2@example.com")
        self.assertEqual(res.data["data"][2]["email"], "user3@example.com")


