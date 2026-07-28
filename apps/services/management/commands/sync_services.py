from django.core.management.base import BaseCommand
from apps.services.services import ServiceSyncService


class Command(BaseCommand):
    help = "Synchronizes locations and services from external appointment APIs into PostgreSQL"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting manual synchronization of locations and services..."))
        sync_service = ServiceSyncService()
        try:
            results = sync_service.sync_all()
            loc_count = results.get("locations_synced", 0)
            svc_count = results.get("services_synced", 0)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully synchronized {loc_count} locations and {svc_count} services."
                )
            )
        except Exception as exc:
            self.stdout.write(self.style.ERROR(f"Service synchronization failed: {exc}"))
