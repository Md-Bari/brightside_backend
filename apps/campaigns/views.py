from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

from apps.common.permissions import IsAdminJWTUser
from apps.common.response import success_response

from .models import Campaign
from .serializers import CampaignSerializer


class AdminCampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    permission_classes = []
    pagination_class = None
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        summary="[Admin] List all campaigns",
        tags=["Admin - Campaigns"],
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response(serializer.data, "Campaigns retrieved.")

    @extend_schema(
        summary="[Admin] Create a new campaign",
        tags=["Admin - Campaigns"],
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return success_response(
            None, "Campaign created successfully.", status.HTTP_201_CREATED
        )

    @extend_schema(
        summary="[Admin] Retrieve a campaign",
        tags=["Admin - Campaigns"],
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(serializer.data, "Campaign retrieved.")

    @extend_schema(
        summary="[Admin] Update a campaign",
        tags=["Admin - Campaigns"],
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return success_response(serializer.data, "Campaign updated successfully.")

    @extend_schema(
        summary="[Admin] Update a campaign (partial)",
        tags=["Admin - Campaigns"],
    )
    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    @extend_schema(
        summary="[Admin] Delete a campaign",
        tags=["Admin - Campaigns"],
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return success_response(None, "Campaign deleted successfully.")


class PublicCampaignListView(generics.ListAPIView):
    queryset = Campaign.objects.filter(is_active=True)
    serializer_class = CampaignSerializer
    permission_classes = []
    pagination_class = None

    @extend_schema(
        summary="List all active campaigns",
        tags=["Public - Campaigns"],
    )
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response(serializer.data, "Active campaigns retrieved.")
