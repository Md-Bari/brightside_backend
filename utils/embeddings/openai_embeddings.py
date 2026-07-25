import logging
import time

from django.conf import settings
from openai import OpenAI

from .base import BaseEmbeddingClient

logger = logging.getLogger("brightside")


class OpenAIEmbeddingClient(BaseEmbeddingClient):
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_EMBEDDING_MODEL

    def embed_text(self, text: str) -> list[float]:
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        start = time.monotonic()
        response = self.client.embeddings.create(model=self.model, input=texts)
        latency_ms = round((time.monotonic() - start) * 1000, 2)
        logger.info("OpenAI embedding latency: %.2fms count=%d", latency_ms, len(texts))
        return [item.embedding for item in response.data]
