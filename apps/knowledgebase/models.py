from django.conf import settings
from django.db import models
from pgvector.django import VectorField, HnswIndex


def kb_upload_path(instance, filename):
    return f"knowledge_base/{filename}"


class KnowledgeFile(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to=kb_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    is_processed = models.BooleanField(default=False)
    processing_error = models.TextField(blank=True, default="")

    class Meta:
        db_table = "knowledge_files"
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.title


class KnowledgeChunk(models.Model):
    knowledge_file = models.ForeignKey(
        KnowledgeFile, related_name="chunks", on_delete=models.CASCADE
    )
    chunk_text = models.TextField()
    chunk_index = models.IntegerField(default=0)
    embedding = VectorField(dimensions=settings.EMBEDDING_DIMENSION)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "knowledge_chunks"
        ordering = ["knowledge_file_id", "chunk_index"]
        indexes = [
            HnswIndex(
                name="knowledge_chunk_embedding_hnsw",
                fields=["embedding"],
                m=16,
                ef_construction=64,
                opclasses=["vector_cosine_ops"],
            ),
        ]

    def __str__(self):
        return f"{self.knowledge_file.title} #{self.chunk_index}"
