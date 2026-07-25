from django.urls import path

from .views import AdminUserListView, AdminUserSessionsListView

urlpatterns = [
    path("", AdminUserListView.as_view(), name="admin-user-list"),
    path(
        "<uuid:user_id>/sessions/",
        AdminUserSessionsListView.as_view(),
        name="admin-user-sessions",
    ),
]
