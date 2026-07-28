# pyrefly: ignore [missing-import]
from drf_spectacular.utils import extend_schema
# pyrefly: ignore [missing-import]
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.common.response import success_response

from .serializers import AdminTokenObtainPairSerializer


class AdminLoginView(TokenObtainPairView):
    serializer_class = AdminTokenObtainPairSerializer

    @extend_schema(summary="Admin login (obtain JWT access/refresh tokens)", tags=["Admin - Auth"])
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return success_response(serializer.validated_data, "Login successful.")


class AdminTokenRefreshView(TokenRefreshView):
    @extend_schema(summary="Refresh admin JWT access token", tags=["Admin - Auth"])
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return success_response(serializer.validated_data, "Token refreshed.")
