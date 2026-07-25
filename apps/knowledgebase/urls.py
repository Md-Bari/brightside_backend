from django.urls import path

from .views import KnowledgeUploadView, KnowledgeListView, KnowledgeDetailDeleteView

urlpatterns = [
    path("upload/", KnowledgeUploadView.as_view(), name="kb-upload"),
    path("", KnowledgeListView.as_view(), name="kb-list"),
    path("<int:pk>/", KnowledgeDetailDeleteView.as_view(), name="kb-detail-delete"),
]
