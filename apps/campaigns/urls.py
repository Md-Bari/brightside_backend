from django.urls import path

from .views import PublicCampaignListView

urlpatterns = [
    path("", PublicCampaignListView.as_view(), name="campaign-list"),
]
