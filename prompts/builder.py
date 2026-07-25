"""
Prompt Builder: assembles the final message list sent to Groq.
Combines: system prompt + conversation history + retrieved KB chunks +
current user question.
"""
from django.conf import settings


def build_messages(history: list[dict], question: str, kb_chunks: list[str] | None = None) -> list[dict]:
    system_prompt = settings.BRIGHTSIDE_SYSTEM_PROMPT

    if kb_chunks:
        context_block = "\n\n".join(f"- {chunk}" for chunk in kb_chunks)
        system_prompt += (
            "\n\nRelevant knowledge base context for this question:\n"
            f"{context_block}\n\n"
            "Use only the context above for Brightside-specific facts. If "
            "it doesn't answer the question, say so honestly."
        )

    messages = [{"role": "system", "content": system_prompt}]
    for turn in history:
        role = turn.get("role")
        content = turn.get("content")
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": question})
    return messages
