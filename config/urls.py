from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from django.views.generic import RedirectView

from django.views.static import serve
from django.urls import re_path

urlpatterns = [
    path("", RedirectView.as_view(url="api/docs/", permanent=False)),
    path("admin/", admin.site.urls),

    # Schema / Docs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),


    # Public + Admin domain APIs
    path("api/v1/sessions/", include("apps.sessions.urls")),
    path("api/v1/admin/sessions/", include("apps.sessions.urls_admin")),
    path("api/v1/chat/", include("apps.chatbot.urls")),
    path("api/v1/admin/kb/", include("apps.knowledgebase.urls")),
    path("api/v1/campaigns/", include("apps.campaigns.urls")),
    path("api/v1/admin/campaigns/", include("apps.campaigns.urls_admin")),
    path("api/v1/admin/users/", include("apps.users.urls")),
]

# Serve media files directly from Django (since Nginx is removed)
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

