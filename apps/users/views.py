from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView

from apps.common.response import success_response
from apps.sessions.models import ChatSession
from apps.sessions.serializers import AdminSessionListSerializer

from .models import CustomerUser
from .serializers import CustomerUserSerializer


class AdminUserListView(APIView):
    permission_classes = []

    @extend_schema(
        responses={200: CustomerUserSerializer(many=True)},
        summary="[Admin] List all chatbot users",
        tags=["Admin - 1. Users"],
    )
    def get(self, request):
        users = CustomerUser.objects.all()
        data = CustomerUserSerializer(users, many=True).data
        return success_response(data, "Users retrieved.")


class AdminUserSessionsListView(APIView):
    permission_classes = []

    @extend_schema(
        responses={200: AdminSessionListSerializer(many=True)},
        summary="[Admin] List all sessions for a specific user",
        tags=["Admin - 2. Sessions"],
    )
    def get(self, request, user_id):
        user = get_object_or_404(CustomerUser, user_id=user_id)
        if user.human_escalation_required:
            user.human_escalation_required = False
            user.save(update_fields=["human_escalation_required", "updated_at"])
        sessions = ChatSession.objects.filter(user=user)
        data = {
            "user_id": str(user.user_id),
            "email": user.email,
            "name": user.name,
            "sessions": AdminSessionListSerializer(sessions, many=True).data,
        }
        return success_response(data, f"Sessions for user {user.email} retrieved.")
