"""
Prompt Builder: assembles the final message list sent to Groq.
Combines: system prompt + conversation history + retrieved KB chunks +
current user question.
"""
from django.conf import settings


def build_messages(
    history: list[dict],
    question: str,
    kb_chunks: list[str] | None = None,
    services_context: str | None = None
) -> list[dict]:
    system_prompt = settings.BRIGHTSIDE_SYSTEM_PROMPT

    if services_context:
        system_prompt += (
            "\n\n=================================================================\n"
            "OFFICIAL SERVICES & LOCATIONS DATA:\n"
            "=================================================================\n"
            f"{services_context}\n"
            "=================================================================\n\n"
            "MANDATORY RESPONSE FORMATTING & HUMAN TONE RULES:\n"
            "1. ALWAYS format your entire response using HTML tags for visual structure (e.g. <b>, <strong>, <br>, <p>, <ul>, <li>).\n"
            "2. ALWAYS speak naturally like a helpful human agent. NEVER use technical phrases like 'according to our database', 'database tables', 'knowledge base', 'KB', or 'Location ID'.\n"
            "3. When answering about locations, state the address directly and cleanly, e.g.:\n"
            "   <b>Brightside Car Wash Location:</b><br>3000 Pennsylvania Ave Nw, Washington, DC 20500\n"
            "4. KNOWLEDGE BASE & COMPANY FACTS: For service pricing and branch locations, use the official services list. For general company questions about Brightside Car Wash (such as founder, company history, mission, or policies), answer accurately and naturally using the retrieved Knowledge Base context.\n"
            "5. SERVICE DETAILS FORMATTING: Whenever you list or describe service details (price, duration, description), you MUST include a dedicated list item (<li>) for Location specifying the branch address, e.g.:\n"
            "   <b>Showroom Detail - Coupe</b><br>\n"
            "   <ul>\n"
            "     <li><b>Price:</b> $100.00</li>\n"
            "     <li><b>Duration:</b> 240 mins</li>\n"
            "     <li><b>Location:</b> 3000 Pennsylvania Ave Nw, Washington, DC 20500</li>\n"
            "     <li><b>Description:</b> Deep interior cleaning, vacuuming, and wax buffing.</li>\n"
            "   </ul>\n"
            "6. If a service or location requested by the customer is NOT on the list above, state politely and naturally that we do not offer it, and share the available services.\n"
            "7. When a customer wants to book a slot, schedule an appointment, or make a reservation, ALWAYS provide the official booking link:\n"
            "   <b>Book Your Slot Online:</b> <a href=\"https://bright-carwash-website.vercel.app/services\" target=\"_blank\">https://bright-carwash-website.vercel.app/services</a>\n"
            "8. OUT-OF-DOMAIN QUESTIONS: If a customer asks an out-of-domain question unrelated to Brightside Car Wash (such as history, recipes, weather, general science, sports, coding, etc.), DO NOT answer it. Politely state using HTML tags that you are unable to answer that question, but welcome them to ask any question about Brightside Car Wash services, pricing, locations, or booking a slot."
        )

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
