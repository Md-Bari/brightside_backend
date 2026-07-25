import logging
import time

import google.generativeai as genai
from django.conf import settings

from .base import BaseEmbeddingClient

logger = logging.getLogger("brightside")


class GeminiEmbeddingClient(BaseEmbeddingClient):
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = settings.GEMINI_EMBEDDING_MODEL

    def embed_text(self, text: str) -> list[float]:
        start = time.monotonic()
        kwargs = {}
        if settings.EMBEDDING_DIMENSION:
            kwargs["output_dimensionality"] = settings.EMBEDDING_DIMENSION
        result = genai.embed_content(model=self.model, content=text, **kwargs)
        latency_ms = round((time.monotonic() - start) * 1000, 2)
        logger.info("Gemini embedding latency: %.2fms", latency_ms)
        return result["embedding"]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_text(t) for t in texts]
