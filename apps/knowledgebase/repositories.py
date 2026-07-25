"""
Repository layer for knowledge base files/chunks, including pgvector
similarity search. All raw ORM/vector queries live here.
"""
from django.utils import timezone
from pgvector.django import CosineDistance

from .models import KnowledgeFile, KnowledgeChunk


class KnowledgeFileRepository:
    def create(self, title: str, file) -> KnowledgeFile:
        return KnowledgeFile.objects.create(title=title, file=file)

    def get_by_id(self, file_id: int) -> KnowledgeFile | None:
        return KnowledgeFile.objects.filter(id=file_id).first()

    def list_all(self):
        return KnowledgeFile.objects.all()

    def delete(self, file_id: int) -> bool:
        deleted, _ = KnowledgeFile.objects.filter(id=file_id).delete()
        return deleted > 0

    def mark_processed(self, file_id: int, success: bool, error: str = ""):
        # .update() bypasses auto_now, so the timestamps are set explicitly.
        now = timezone.now()
        KnowledgeFile.objects.filter(id=file_id).update(
            is_processed=success,
            processing_error=error,
            processed_at=now,
            updated_at=now,
        )


class KnowledgeChunkRepository:
    def bulk_create(self, chunks: list[KnowledgeChunk]) -> None:
        KnowledgeChunk.objects.bulk_create(chunks, batch_size=100)

    def delete_for_file(self, file_id: int) -> None:
        KnowledgeChunk.objects.filter(knowledge_file_id=file_id).delete()

    def similarity_search(self, query_embedding: list[float], top_k: int = 4):
        """
        Returns the top_k most similar chunks using cosine distance via
        pgvector's HNSW index.
        """
        return (
            KnowledgeChunk.objects.annotate(
                distance=CosineDistance("embedding", query_embedding)
            )
            .order_by("distance")[:top_k]
        )
