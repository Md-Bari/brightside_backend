from django.urls import path

from .views import KnowledgeUploadView, KnowledgeListView, KnowledgeDetailDeleteView, WebsiteScrapeView

urlpatterns = [
    path("upload/", KnowledgeUploadView.as_view(), name="kb-upload"),
    path("scrape-website/", WebsiteScrapeView.as_view(), name="kb-scrape-website"),
    path("", KnowledgeListView.as_view(), name="kb-list"),
    path("<int:pk>/", KnowledgeDetailDeleteView.as_view(), name="kb-detail-delete"),
]
