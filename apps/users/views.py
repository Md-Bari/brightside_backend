from django.db import models
from django.shortcuts import get_object_or_404
# pyrefly: ignore [missing-import]
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.views import APIView

from apps.common.pagination import CustomCursorPagination
from apps.common.response import success_response
from apps.sessions.models import ChatSession
from apps.sessions.serializers import AdminSessionListSerializer

from .models import CustomerUser
from .serializers import CustomerUserSerializer


class UserListCursorPagination(CustomCursorPagination):
    ordering = ("-last_chat_activity", "-created_at")


class AdminUserListView(APIView):
    permission_classes = []

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="search",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Search query to filter users by name or email.",
            ),
            OpenApiParameter(
                name="cursor",
                type=str,
                location=OpenApiParameter.QUERY,
                description="The pagination cursor value.",
            ),
            OpenApiParameter(
                name="page_size",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Number of results to return per page.",
            ),
        ],
        responses={200: CustomerUserSerializer(many=True)},
        summary="[Admin] List all chatbot users with search and cursor pagination",
        tags=["Admin - 1. Users"],
    )
    def get(self, request):
        from django.db.models import Max
        from django.db.models.functions import Coalesce

        search_query = request.query_params.get("search", "")
        users = CustomerUser.objects.annotate(
            last_chat_activity=Coalesce(Max("sessions__updated_at"), "created_at")
        )

        if search_query:
            users = users.filter(
                models.Q(name__icontains=search_query) | models.Q(email__icontains=search_query)
            )

        paginator = UserListCursorPagination()
        page = paginator.paginate_queryset(users, request, view=self)
        if page is not None:
            serializer = CustomerUserSerializer(page, many=True)
            meta = {
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
                "page_size": paginator.get_page_size(request),
            }
            return success_response(serializer.data, "Users retrieved.", meta=meta)

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
