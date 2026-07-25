"""
Business logic for customer identification.
Workflow: if the email exists, load the user; otherwise create it.
"""
import logging

from .repositories import UserRepository

logger = logging.getLogger("brightside")


class UserService:
    def __init__(self, repository: UserRepository | None = None):
        self.repository = repository or UserRepository()

    def get_or_create_user(self, email: str, name: str = ""):
        email = email.strip().lower()
        user = self.repository.get_by_email(email)
        if user:
            if name and not user.name:
                user.name = name
                user.save(update_fields=["name", "updated_at"])
            logger.debug("Loaded existing user: %s", email)
            return user
        user = self.repository.create(email, name=name)
        logger.info("Created new user: %s", email)
        return user
