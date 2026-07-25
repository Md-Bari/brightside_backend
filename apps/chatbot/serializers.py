from rest_framework import serializers


class ChatMessageRequestSerializer(serializers.Serializer):
    session_id = serializers.UUIDField()
    message = serializers.CharField(allow_blank=False, trim_whitespace=True)


class ChatMessageResponseSerializer(serializers.Serializer):
    session_id = serializers.UUIDField()
    user_id = serializers.UUIDField()
    question_type = serializers.ChoiceField(choices=["DOMAIN", "GENERAL"])
    answer = serializers.CharField()
    messages = serializers.ListField(child=serializers.DictField())
