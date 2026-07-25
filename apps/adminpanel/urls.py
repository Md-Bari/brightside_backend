from django.urls import path

from .views import AdminLoginView, AdminTokenRefreshView

urlpatterns = [
    path("login/", AdminLoginView.as_view(), name="admin-login"),
    path("refresh/", AdminTokenRefreshView.as_view(), name="admin-token-refresh"),
]
