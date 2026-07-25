from rest_framework import serializers
from apps.campaigns.models import Campaign
from apps.campaigns.serializers import CampaignSerializer
from .models import ChatSession


class CreateSessionRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    name = serializers.CharField(required=False, allow_blank=True, default="")


class SessionSerializer(serializers.ModelSerializer):
    campaigns = serializers.SerializerMethodField()
    # session.user_id is the customer's UUID itself — no join needed.
    user_id = serializers.UUIDField(read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = ChatSession
        fields = ["session_id", "user_id", "email", "status", "created_at", "messages", "campaigns"]
        read_only_fields = fields

    def get_campaigns(self, obj):
        active_campaigns = Campaign.objects.filter(is_active=True)
        return CampaignSerializer(active_campaigns, many=True, context=self.context).data


class EndSessionRequestSerializer(serializers.Serializer):
    session_id = serializers.UUIDField()


class EndSessionResponseSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = ChatSession
        fields = ["session_id", "user_id", "email", "status", "ended_at"]
        read_only_fields = fields


class AdminSessionListSerializer(serializers.ModelSerializer):
    """Dashboard level 2: the sessions belonging to one user."""

    message_count = serializers.SerializerMethodField()

    class Meta:
        model = ChatSession
        fields = ["session_id", "status", "message_count", "created_at", "updated_at", "ended_at"]
        read_only_fields = fields

    def get_message_count(self, obj):
        return len(obj.messages or [])


class AdminSessionDetailSerializer(serializers.ModelSerializer):
    """Dashboard level 3: the full JSONB conversation of one session."""

    user_id = serializers.UUIDField(read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = ChatSession
        fields = [
            "session_id", "user_id", "email", "status", "messages",
            "created_at", "updated_at", "ended_at",
        ]
        read_only_fields = fields
