"""
Knowledge Base pipeline: upload -> extract -> clean -> chunk -> embed -> store.
Also exposes retrieval for RAG.
"""
import logging

from django.conf import settings
from django.utils import timezone

from apps.common.exceptions import ServiceError, NotFoundServiceError
from utils.embeddings.base import get_embedding_client
from utils.text_processing.extractors import extract_text, UnsupportedFileTypeError
from utils.text_processing.cleaning import clean_text
from utils.text_processing.chunking import chunk_text

from .models import KnowledgeChunk
from .repositories import KnowledgeFileRepository, KnowledgeChunkRepository

logger = logging.getLogger("brightside")


class KnowledgeBaseService:
    def __init__(self, file_repo=None, chunk_repo=None, embedding_client=None):
        self.file_repo = file_repo or KnowledgeFileRepository()
        self.chunk_repo = chunk_repo or KnowledgeChunkRepository()
        self.embedding_client = embedding_client or get_embedding_client()

    def upload_and_process(self, title: str, uploaded_file):
        title = title or uploaded_file.name
        knowledge_file = self.file_repo.create(title=title, file=uploaded_file)

        try:
            raw_text = extract_text(knowledge_file.file.path)
            cleaned = clean_text(raw_text)
            text_chunks = chunk_text(
                cleaned,
                chunk_size=settings.KB_CHUNK_SIZE,
                overlap=settings.KB_CHUNK_OVERLAP,
            )

            if not text_chunks:
                raise ServiceError("No extractable text found in the uploaded file.")

            embeddings = self.embedding_client.embed_batch(text_chunks)

            chunk_objects = [
                KnowledgeChunk(
                    knowledge_file=knowledge_file,
                    chunk_text=chunk,
                    chunk_index=idx,
                    embedding=embedding,
                    metadata={"source": knowledge_file.title},
                )
                for idx, (chunk, embedding) in enumerate(zip(text_chunks, embeddings))
            ]
            self.chunk_repo.bulk_create(chunk_objects)
            self.file_repo.mark_processed(knowledge_file.id, success=True)
            logger.info(
                "Processed knowledge file '%s' into %d chunks", title, len(chunk_objects)
            )

        except UnsupportedFileTypeError as exc:
            self.file_repo.mark_processed(knowledge_file.id, success=False, error=str(exc))
            raise ServiceError(str(exc)) from exc
        except Exception as exc:
            logger.exception("Failed to process knowledge file '%s'", title)
            self.file_repo.mark_processed(knowledge_file.id, success=False, error=str(exc))
            raise ServiceError(f"Failed to process knowledge file: {exc}") from exc

        return self.file_repo.get_by_id(knowledge_file.id)

    def process_raw_text(self, title: str, filename: str, content_text: str):
        from django.core.files.base import ContentFile
        from .models import KnowledgeFile

        # Delete old file with same title if present
        existing_files = KnowledgeFile.objects.filter(title=title)
        for old_file in existing_files:
            try:
                self.delete_file(old_file.id)
            except Exception as e:
                logger.warning("Failed to delete existing KB file '%s': %s", old_file.id, e)

        file_obj = ContentFile(content_text.encode("utf-8"), name=filename)
        knowledge_file = self.file_repo.create(title=title, file=file_obj)

        try:
            cleaned = clean_text(content_text)
            text_chunks = chunk_text(
                cleaned,
                chunk_size=settings.KB_CHUNK_SIZE,
                overlap=settings.KB_CHUNK_OVERLAP,
            )

            if not text_chunks:
                raise ServiceError("No extractable text found in the content.")

            embeddings = self.embedding_client.embed_batch(text_chunks)

            chunk_objects = [
                KnowledgeChunk(
                    knowledge_file=knowledge_file,
                    chunk_text=chunk,
                    chunk_index=idx,
                    embedding=embedding,
                    metadata={"source": knowledge_file.title},
                )
                for idx, (chunk, embedding) in enumerate(zip(text_chunks, embeddings))
            ]
            self.chunk_repo.bulk_create(chunk_objects)
            self.file_repo.mark_processed(knowledge_file.id, success=True)
            logger.info("Processed raw text KB file '%s' into %d chunks", title, len(chunk_objects))

        except Exception as exc:
            logger.exception("Failed to process raw text KB file '%s'", title)
            self.file_repo.mark_processed(knowledge_file.id, success=False, error=str(exc))
            raise ServiceError(f"Failed to process knowledge text: {exc}") from exc

        return self.file_repo.get_by_id(knowledge_file.id)


    def list_files(self):
        return self.file_repo.list_all()

    def get_file(self, file_id: int):
        file = self.file_repo.get_by_id(file_id)
        if not file:
            raise NotFoundServiceError("Knowledge file not found.")
        return file

    def delete_file(self, file_id: int) -> dict:
        file = self.get_file(file_id)
        title = file.title
        if not self.file_repo.delete(file_id):
            raise NotFoundServiceError("Knowledge file not found.")
        return {"id": file_id, "title": title, "deleted_at": timezone.now()}

    def retrieve_relevant_chunks(self, question: str, top_k: int | None = None) -> list[str]:
        top_k = top_k or settings.KB_TOP_K
        query_embedding = self.embedding_client.embed_text(question)
        results = self.chunk_repo.similarity_search(query_embedding, top_k=top_k)
        return [chunk.chunk_text for chunk in results]
