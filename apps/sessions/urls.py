from django.urls import path

from .views import (
    CreateSessionView,
)

urlpatterns = [
    # Public
    path("", CreateSessionView.as_view(), name="session-create"),
]
