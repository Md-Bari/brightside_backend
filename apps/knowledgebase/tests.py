from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient


class KnowledgeBaseAdminAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_knowledge_files_empty(self):
        response = self.client.get("/api/v1/admin/kb/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"], [])

    def test_kb_endpoints_do_not_require_admin_auth(self):
        response = self.client.get("/api/v1/admin/kb/")
        self.assertEqual(response.status_code, 200)
