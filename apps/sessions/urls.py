from django.urls import path

from .views import (
    CreateSessionView,
    EndSessionView,
)

urlpatterns = [
    # Public
    path("", CreateSessionView.as_view(), name="session-create"),
    path("end/", EndSessionView.as_view(), name="session-end"),
]
