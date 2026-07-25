"""
Embedding provider abstraction. Configure via EMBEDDING_PROVIDER env var
("openai" or "gemini"). Both providers implement the same interface so the
rest of the app (knowledge base pipeline, RAG search) never needs to know
which one is active.
"""
import logging
from abc import ABC, abstractmethod

from django.conf import settings

logger = logging.getLogger("brightside")


class BaseEmbeddingClient(ABC):
    @abstractmethod
    def embed_text(self, text: str) -> list[float]:
        ...

    @abstractmethod
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        ...


def get_embedding_client() -> BaseEmbeddingClient:
    provider = (settings.EMBEDDING_PROVIDER or "openai").lower()
    if provider == "gemini":
        from .gemini_embeddings import GeminiEmbeddingClient
        return GeminiEmbeddingClient()
    from .openai_embeddings import OpenAIEmbeddingClient
    return OpenAIEmbeddingClient()
