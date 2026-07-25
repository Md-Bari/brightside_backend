from rest_framework.permissions import BasePermission


class IsAdminJWTUser(BasePermission):
    """
    Grants access only to authenticated Django staff/superusers via JWT.
    Used to protect all /api/v1/admin/* endpoints.
    """

    message = "Admin authentication required."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and (user.is_staff or user.is_superuser))
