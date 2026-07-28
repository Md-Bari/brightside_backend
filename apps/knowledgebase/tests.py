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

    def test_upload_csv_success(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        csv_content = b"header1,header2\nrow1col1,row1col2\n"
        uploaded_file = SimpleUploadedFile("knowledge.csv", csv_content, content_type="text/csv")

        response = self.client.post(
            "/api/v1/admin/kb/upload/",
            {"title": "Test CSV", "file": uploaded_file},
            format="multipart"
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data["data"]["is_processed"])

        from apps.knowledgebase.models import KnowledgeChunk
        chunks = KnowledgeChunk.objects.filter(knowledge_file_id=response.data["data"]["id"])
        self.assertTrue(chunks.exists())
        self.assertIn("header1 | header2", chunks[0].chunk_text)
        self.assertIn("row1col1 | row1col2", chunks[0].chunk_text)

    def test_upload_xlsx_success(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        from openpyxl import Workbook
        import io

        wb = Workbook()
        ws = wb.active
        ws.title = "MainSheet"
        ws.append(["Name", "Wash Type", "Price"])
        ws.append(["Alice", "Ultimate", "$25"])

        xlsx_io = io.BytesIO()
        wb.save(xlsx_io)
        xlsx_io.seek(0)

        uploaded_file = SimpleUploadedFile(
            "wash_menu.xlsx",
            xlsx_io.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        response = self.client.post(
            "/api/v1/admin/kb/upload/",
            {"title": "Wash Menu", "file": uploaded_file},
            format="multipart"
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data["data"]["is_processed"])

        from apps.knowledgebase.models import KnowledgeChunk
        chunks = KnowledgeChunk.objects.filter(knowledge_file_id=response.data["data"]["id"])
        self.assertTrue(chunks.exists())
        self.assertIn("MainSheet", chunks[0].chunk_text)
        self.assertIn("Alice | Ultimate | $25", chunks[0].chunk_text)

    def test_xls_extraction(self):
        from unittest.mock import patch, MagicMock
        from utils.text_processing.extractors import _extract_xls

        mock_sheet = MagicMock()
        mock_sheet.name = "SheetXLS"
        mock_sheet.nrows = 2
        mock_sheet.row_values.side_effect = [
            ["Col1", "Col2"],
            ["Val1", "Val2"]
        ]

        mock_wb = MagicMock()
        mock_wb.nsheets = 1
        mock_wb.sheet_by_index.return_value = mock_sheet

        with patch("xlrd.open_workbook", return_value=mock_wb) as mock_open:
            result = _extract_xls("mock_file.xls")
            self.assertIn("SheetXLS", result)
            self.assertIn("Col1 | Col2", result)
            self.assertIn("Val1 | Val2", result)
            mock_open.assert_called_once_with("mock_file.xls")

    def test_get_knowledge_file_detail_without_chunks(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        csv_content = b"header1,header2\nrow1col1,row1col2\n"
        uploaded_file = SimpleUploadedFile("detail_test.csv", csv_content, content_type="text/csv")

        upload_res = self.client.post(
            "/api/v1/admin/kb/upload/",
            {"title": "Detail Test", "file": uploaded_file},
            format="multipart"
        )
        file_id = upload_res.data["data"]["id"]

        detail_res = self.client.get(f"/api/v1/admin/kb/{file_id}/")
        self.assertEqual(detail_res.status_code, 200)
        self.assertIn("file", detail_res.data["data"])
        self.assertNotIn("chunks", detail_res.data["data"])

