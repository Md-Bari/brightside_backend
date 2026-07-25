"""
Thin wrapper around the Groq Chat Completions API.
Isolated here so the rest of the codebase depends on an abstraction,
not directly on the Groq SDK (Dependency Inversion Principle).
"""
import logging
import time

from django.conf import settings
from groq import Groq

logger = logging.getLogger("brightside")

_client = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        _client = Groq(api_key=settings.GROQ_API_KEY)
    return _client


class GroqClientError(Exception):
    pass


def generate_chat_completion(messages: list[dict], model: str | None = None,
                              temperature: float = 0.3, max_tokens: int = 1024) -> str:
    """
    messages: list of {"role": "system"|"user"|"assistant", "content": "..."}
    Returns the assistant's text response.
    """
    model = model or settings.GROQ_MODEL
    client = _get_client()

    start = time.monotonic()
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    except Exception as exc:  # pragma: no cover - network dependent
        logger.error("Groq API call failed: %s", exc)
        raise GroqClientError(str(exc)) from exc
    finally:
        latency_ms = round((time.monotonic() - start) * 1000, 2)
        logger.info("Groq latency: %.2fms model=%s", latency_ms, model)

    return completion.choices[0].message.content.strip()
