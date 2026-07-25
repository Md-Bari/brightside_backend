"""
Public chat endpoint. Protected by UUID session validation (not JWT).
"""
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView

from apps.common.response import success_response

from .serializers import ChatMessageRequestSerializer, ChatMessageResponseSerializer
from .services import ChatService


class ChatMessageView(APIView):
    permission_classes = []

    @extend_schema(
        request=ChatMessageRequestSerializer,
        responses={200: ChatMessageResponseSerializer},
        summary="Send a chat message within an active session",
        tags=["Public - Chat"],
    )
    def post(self, request):
        serializer = ChatMessageRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = ChatService()
        result = service.handle_message(
            session_id=serializer.validated_data["session_id"],
            message=serializer.validated_data["message"],
        )
        return success_response(result, "Message processed successfully.")
