import uuid
from django.db import models


class CustomerUser(models.Model):
    """
    A Brightside chatbot end-user, identified by email, name, and user_id.
    Not related to Django's auth User model, which is reserved for
    admin/staff JWT authentication.

    ``user_id`` is the primary key: there is no separate surrogate integer
    id, so the UUID is the one and only identifier for a customer.
    """

    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    name = models.CharField(max_length=255, blank=True, default="")
    human_escalation_required = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "customer_users"
        ordering = ["-created_at"]

    def __str__(self):
        return self.email
