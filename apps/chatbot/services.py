"""
Chat orchestration service. Implements the full message workflow:

Load JSONB -> append user message -> classify -> (RAG if DOMAIN) ->
build prompt -> call Groq -> append assistant message -> save JSONB ->
return response.
"""
import logging

from apps.common.exceptions import ServiceError
from apps.knowledgebase.services import KnowledgeBaseService
from apps.sessions.services import SessionService
from prompts.builder import build_messages
from utils.llm.groq_client import generate_chat_completion, GroqClientError

from .classifier import QuestionClassifierService

logger = logging.getLogger("brightside")


class ChatService:
    def __init__(
        self,
        session_service: SessionService | None = None,
        kb_service: KnowledgeBaseService | None = None,
        classifier: QuestionClassifierService | None = None,
    ):
        self.session_service = session_service or SessionService()
        self.kb_service = kb_service or KnowledgeBaseService()
        self.classifier = classifier or QuestionClassifierService()

    def handle_message(self, session_id, message: str) -> dict:
        session = self.session_service.get_active_session(session_id)

        # 1. Load JSONB history (before appending the new message)
        history = list(session.messages or [])

        # 2. Append user message
        session = self.session_service.append_message(session, "user", message)

        # 3. Classify
        question_type = self.classifier.classify(message)
        logger.info("Session %s classified as %s", session_id, question_type)

        # 4. Retrieve KB context if DOMAIN
        kb_chunks = []
        if question_type == QuestionClassifierService.DOMAIN:
            kb_chunks = self.kb_service.retrieve_relevant_chunks(message)

        # 5. Build prompt (system + history + kb context + question)
        llm_messages = build_messages(history=history, question=message, kb_chunks=kb_chunks)

        # 6. Call Groq
        try:
            answer = generate_chat_completion(messages=llm_messages)
        except GroqClientError as exc:
            raise ServiceError(f"AI service is currently unavailable: {exc}", status_code=503) from exc

        # Detect human escalation
        if "[HUMAN_ESCALATION]" in answer or "I am unable to assist with this query. Our staff will communicate with you very soon." in answer:
            user = session.user
            user.human_escalation_required = True
            user.save(update_fields=["human_escalation_required", "updated_at"])
            answer = answer.replace("[HUMAN_ESCALATION]", "").strip()
            if not answer:
                answer = "Our staff will communicate with you very soon."

        # 7. Append assistant message + save
        session = self.session_service.append_message(session, "assistant", answer)

        return {
            "session_id": str(session.session_id),
            "user_id": str(session.user_id),
            "question_type": question_type,
            "answer": answer,
            "messages": session.messages,
        }
