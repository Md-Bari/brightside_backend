from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import AdminCampaignViewSet

router = DefaultRouter()
router.register("", AdminCampaignViewSet, basename="admin-campaign")

urlpatterns = [
    path("", include(router.urls)),
]
