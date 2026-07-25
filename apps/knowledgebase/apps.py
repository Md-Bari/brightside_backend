from django.apps import AppConfig


class KnowledgebaseConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.knowledgebase"

    def ready(self):
        # Ensure pgvector extension is registered before first migration.
        pass
