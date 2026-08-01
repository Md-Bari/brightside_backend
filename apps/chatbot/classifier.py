"""
Question Classifier: decides whether an incoming user message is a
DOMAIN question (should be answered using the Brightside knowledge base
via pgvector RAG) or a GENERAL question (answered directly by Groq).
"""
import logging

from utils.llm.groq_client import generate_chat_completion, GroqClientError

logger = logging.getLogger("brightside")

CLASSIFIER_SYSTEM_PROMPT = (
    "You are a strict classifier for a car wash company's chatbot. "
    "Classify the user's message into exactly one label: DOMAIN or GENERAL.\n"
    "DOMAIN = the question is about Brightside Car Wash specifically "
    "(services, pricing, packages, locations, hours, memberships, "
    "booking, policies, offers, vehicles handled, founder, company history, "
    "mission, etc.) or could plausibly be answered using Brightside's knowledge base. "
    "This includes questions using referential phrases (like 'this company', 'your company', "
    "'this car wash', 'you guys', 'here', 'the founder', etc.) to refer to the business.\n"
    "GENERAL = small talk, greetings, or any question unrelated to "
    "Brightside Car Wash's business.\n"
    "Respond with only one word: DOMAIN or GENERAL."
)


class QuestionClassifierService:
    DOMAIN = "DOMAIN"
    GENERAL = "GENERAL"

    def classify(self, question: str) -> str:
        try:
            result = generate_chat_completion(
                messages=[
                    {"role": "system", "content": CLASSIFIER_SYSTEM_PROMPT},
                    {"role": "user", "content": question},
                ],
                temperature=0.0,
                max_tokens=5,
            )
            label = result.strip().upper()
            if self.DOMAIN in label:
                return self.DOMAIN
            if self.GENERAL in label:
                return self.GENERAL
            logger.warning("Unexpected classifier output '%s', defaulting to DOMAIN", result)
            return self.DOMAIN
        except GroqClientError:
            logger.warning("Classifier LLM call failed; defaulting to DOMAIN")
            return self.DOMAIN
