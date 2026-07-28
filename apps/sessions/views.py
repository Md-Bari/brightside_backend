"""
Session endpoints.
Public: create session, end session (UUID-based, no JWT).
Admin: list/detail/delete sessions (JWT protected).
"""
# pyrefly: ignore [missing-import]
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.common.permissions import IsAdminJWTUser
from apps.common.response import success_response

from .serializers import (
    CreateSessionRequestSerializer,
    SessionSerializer,
    AdminSessionListSerializer,
    AdminSessionDetailSerializer,
)
from .services import SessionService


class CreateSessionView(APIView):
    permission_classes = []

    @extend_schema(
        request=CreateSessionRequestSerializer,
        responses={201: SessionSerializer},
        summary="Create a new chat session for an email",
        tags=["Public - Sessions"],
    )
    def post(self, request):
        serializer = CreateSessionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = SessionService()
        session = service.create_session(
            email=serializer.validated_data["email"],
            name=serializer.validated_data.get("name", ""),
        )
        data = SessionSerializer(session, context={"request": request}).data
        return success_response(data, "Session created successfully.", status.HTTP_201_CREATED)


class AdminSessionDetailView(APIView):
    permission_classes = []

    @extend_schema(
        responses={200: AdminSessionDetailSerializer},
        summary="[Admin] Retrieve a session's full conversation",
        tags=["Admin - 3. Chats"],
    )
    def get(self, request, session_id):
        service = SessionService()
        session = service.get_session(session_id)
        data = AdminSessionDetailSerializer(session).data
        return success_response(data, "Session retrieved.")
