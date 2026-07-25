"""
Repository layer: all ORM operations for CustomerUser live here.
Services must never touch the ORM directly.
"""
from .models import CustomerUser


class UserRepository:
    def get_by_email(self, email: str) -> CustomerUser | None:
        return CustomerUser.objects.filter(email__iexact=email).first()

    def create(self, email: str, name: str = "") -> CustomerUser:
        return CustomerUser.objects.create(email=email, name=name)

    def get_or_create(self, email: str, name: str = "") -> tuple[CustomerUser, bool]:
        return CustomerUser.objects.get_or_create(email__iexact=email, defaults={"email": email, "name": name})
