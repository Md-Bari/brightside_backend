from rest_framework import serializers

from .models import CustomerUser


class CustomerUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerUser
        fields = [
            "user_id", "email", "name", "human_escalation_required",
            "created_at", "updated_at",
        ]
        read_only_fields = fields
