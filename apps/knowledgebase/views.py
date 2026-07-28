"""
Admin Knowledge Base APIs. Protected by JWT (IsAdminJWTUser).
Views contain no business logic; they delegate to KnowledgeBaseService.
"""
import logging

# pyrefly: ignore [missing-import]
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.common.permissions import IsAdminJWTUser
from apps.common.response import success_response

from .serializers import (
    KnowledgeFileUploadSerializer,
    KnowledgeFileSerializer,
    KnowledgeFileDetailSerializer,
)
from .services import KnowledgeBaseService

logger = logging.getLogger("brightside")


class KnowledgeUploadView(APIView):
    permission_classes = []
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        request=KnowledgeFileUploadSerializer,
        responses={201: KnowledgeFileSerializer},
        summary="Upload a knowledge base document (PDF/DOCX/TXT/CSV/EXCEL)",
        tags=["Admin - Knowledge Base"],
    )
    def post(self, request):
        serializer = KnowledgeFileUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = KnowledgeBaseService()
        knowledge_file = service.upload_and_process(
            title=serializer.validated_data.get("title", ""),
            uploaded_file=serializer.validated_data["file"],
        )
        data = KnowledgeFileSerializer(knowledge_file, context={"request": request}).data
        return success_response(data, "Knowledge file uploaded and processed.", status.HTTP_201_CREATED)


class KnowledgeListView(APIView):
    permission_classes = []

    @extend_schema(
        responses={200: KnowledgeFileSerializer(many=True)},
        summary="List all uploaded knowledge base files",
        tags=["Admin - Knowledge Base"],
    )
    def get(self, request):
        service = KnowledgeBaseService()
        files = service.list_files()
        data = KnowledgeFileSerializer(files, many=True, context={"request": request}).data
        return success_response(data, "Knowledge files retrieved.")


class KnowledgeDetailDeleteView(APIView):
    permission_classes = []

    @extend_schema(
        responses={200: KnowledgeFileSerializer},
        summary="Retrieve a single knowledge base file",
        tags=["Admin - Knowledge Base"],
    )
    def get(self, request, pk):
        service = KnowledgeBaseService()
        file = service.get_file(pk)
        data = KnowledgeFileSerializer(file, context={"request": request}).data
        return success_response(data, "Knowledge file retrieved.")

    @extend_schema(
        responses={200: None},
        summary="Delete a knowledge base file and its chunks",
        tags=["Admin - Knowledge Base"],
    )
    def delete(self, request, pk):
        service = KnowledgeBaseService()
        data = service.delete_file(pk)
        return success_response(data, "Knowledge file deleted.")
