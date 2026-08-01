import sys
from django.apps import AppConfig


class ServicesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.services"
    verbose_name = "Car Wash Services & Locations"

    def ready(self):
        disable_commands = {"test", "migrate", "makemigrations", "collectstatic", "createsuperuser", "shell"}
        if any(cmd in sys.argv for cmd in disable_commands):
            return

        from .scheduler import start_service_scheduler
        start_service_scheduler()
