"""
LLM Completion Client abstraction supporting both OpenAI and Groq providers.
Supports switching via LLM_PROVIDER in settings/env.
"""
import logging
import time

from django.conf import settings
from groq import Groq
import openai

logger = logging.getLogger("brightside")

_groq_client = None
_openai_client = None


def _get_groq_client() -> Groq:
    global _groq_client
    if _groq_client is None:
        _groq_client = Groq(api_key=settings.GROQ_API_KEY)
    return _groq_client


def _get_openai_client() -> openai.OpenAI:
    global _openai_client
    if _openai_client is None:
        _openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    return _openai_client


class GroqClientError(Exception):
    """Backwards-compatible exception alias for LLM completion errors."""
    pass


def generate_chat_completion(
    messages: list[dict],
    model: str | None = None,
    temperature: float = 0.3,
    max_tokens: int = 1024
) -> str:
    """
    Generates chat completion via configured provider (OpenAI or Groq).
    messages: list of {"role": "system"|"user"|"assistant", "content": "..."}
    Returns the assistant's text response.
    """
    provider = getattr(settings, "LLM_PROVIDER", "openai").lower()
    start = time.monotonic()

    try:
        if provider == "openai" or (getattr(settings, "OPENAI_API_KEY", "") and not getattr(settings, "GROQ_API_KEY", "")):
            target_model = model or getattr(settings, "OPENAI_MODEL", "gpt-4o-mini")
            client = _get_openai_client()
            completion = client.chat.completions.create(
                model=target_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            provider_name = "OpenAI"
        else:
            target_model = model or settings.GROQ_MODEL
            client = _get_groq_client()
            completion = client.chat.completions.create(
                model=target_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            provider_name = "Groq"

    except Exception as exc:
        logger.error("LLM API call (%s) failed: %s", provider, exc)
        raise GroqClientError(str(exc)) from exc
    finally:
        latency_ms = round((time.monotonic() - start) * 1000, 2)
        logger.info("%s LLM latency: %.2fms model=%s", provider_name if 'provider_name' in locals() else provider, latency_ms, target_model if 'target_model' in locals() else model)

    return completion.choices[0].message.content.strip()
