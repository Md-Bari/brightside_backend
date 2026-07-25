from rest_framework import serializers

from .models import KnowledgeFile, KnowledgeChunk


class KnowledgeFileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeFile
        fields = ["id", "title", "file"]
        extra_kwargs = {"title": {"required": False}}

    def validate_file(self, value):
        allowed_ext = (".pdf", ".docx", ".txt")
        if not value.name.lower().endswith(allowed_ext):
            raise serializers.ValidationError(
                "Unsupported file type. Allowed: PDF, DOCX, TXT."
            )
        return value


class KnowledgeChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeChunk
        fields = ["id", "chunk_index", "chunk_text", "metadata", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class KnowledgeFileSerializer(serializers.ModelSerializer):
    chunk_count = serializers.IntegerField(source="chunks.count", read_only=True)

    class Meta:
        model = KnowledgeFile
        fields = [
            "id", "title", "file", "uploaded_at", "updated_at", "processed_at",
            "is_processed", "processing_error", "chunk_count",
        ]
        read_only_fields = [
            "uploaded_at", "updated_at", "processed_at", "is_processed",
            "processing_error", "chunk_count",
        ]


class KnowledgeFileDetailSerializer(KnowledgeFileSerializer):
    chunks = KnowledgeChunkSerializer(many=True, read_only=True)

    class Meta(KnowledgeFileSerializer.Meta):
        fields = KnowledgeFileSerializer.Meta.fields + ["chunks"]
