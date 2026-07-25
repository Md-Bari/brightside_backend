from django.urls import path

from .views import AdminSessionDetailView

urlpatterns = [
    path("<uuid:session_id>/", AdminSessionDetailView.as_view(), name="admin-session-detail"),
]
