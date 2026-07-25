from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient


class ChatMessageAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        create_resp = self.client.post(
            "/api/v1/sessions/", {"email": "chatuser@brightside.com"}, format="json"
        )
        self.session_id = create_resp.data["data"]["session_id"]

    @patch("apps.chatbot.services.generate_chat_completion")
    @patch("apps.chatbot.classifier.generate_chat_completion")
    def test_general_question_skips_knowledge_base(self, mock_classify_call, mock_answer_call):
        mock_classify_call.return_value = "GENERAL"
        mock_answer_call.return_value = "Hello! How can I help you today?"

        response = self.client.post(
            "/api/v1/chat/message/",
            {"session_id": self.session_id, "message": "Hi there"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"]["question_type"], "GENERAL")
        self.assertEqual(response.data["data"]["answer"], "Hello! How can I help you today?")

    def test_message_to_invalid_session_returns_404(self):
        response = self.client.post(
            "/api/v1/chat/message/",
            {"session_id": "0" * 32, "message": "Hi"},
            format="json",
        )
        self.assertEqual(response.status_code, 404)
