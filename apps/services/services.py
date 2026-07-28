"""
Service Synchronization Service layer.
Handles HTTP requests to external appointment APIs and coordinates DB persistence.
"""
import logging
import urllib.request
import json
from typing import Dict, List, Any

from django.conf import settings
from .repositories import LocationRepository, ServiceRepository

logger = logging.getLogger("brightside")


class ServiceSyncService:
    def __init__(
        self,
        location_repo: LocationRepository | None = None,
        service_repo: ServiceRepository | None = None,
        base_url: str | None = None,
    ):
        self.location_repo = location_repo or LocationRepository()
        self.service_repo = service_repo or ServiceRepository()
        self.base_url = (base_url or getattr(settings, "APPOINTMENTS_API_BASE_URL", "https://tooth-availability-coupons-stays.trycloudflare.com")).rstrip("/")

    def _http_get_json(self, url: str) -> Dict[str, Any]:
        """Helper to fetch JSON data via HTTP GET request."""
        headers = {"User-Agent": "Brightside-Backend/1.0", "Accept": "application/json"}
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=20) as response:
                if response.status != 200:
                    raise IOError(f"HTTP GET {url} failed with status {response.status}")
                body = response.read().decode("utf-8")
                return json.loads(body)
        except Exception as exc:
            logger.error("Failed to fetch data from %s: %s", url, exc)
            raise IOError(f"Error fetching API data from {url}: {exc}") from exc

    def fetch_locations(self) -> List[Dict[str, Any]]:
        """Fetch location records from the external appointments API."""
        url = f"{self.base_url}/api/appointments/locations"
        logger.info("Syncing locations from URL: %s", url)
        payload = self._http_get_json(url)
        if not payload.get("success"):
            logger.warning("Locations API returned unsuccessful payload: %s", payload)
            return []
        return payload.get("data", [])

    def fetch_services_for_location(self, location_id: str) -> List[Dict[str, Any]]:
        """Fetch service records for a specific locationId from external appointments API."""
        url = f"{self.base_url}/api/appointments/services?locationId={location_id}"
        logger.info("Syncing services for locationId %s from URL: %s", location_id, url)
        payload = self._http_get_json(url)
        if not payload.get("success"):
            logger.warning("Services API returned unsuccessful payload for locationId %s: %s", location_id, payload)
            return []
        return payload.get("data", [])

    def sync_all(self) -> Dict[str, int]:
        """
        Orchestrates full synchronization:
        1. Fetches all locations and saves to Location DB table.
        2. For each location, fetches services and saves to Service DB table.
        """
        locations_data = self.fetch_locations()
        synced_locations_count = 0
        synced_services_count = 0

        for loc_data in locations_data:
            try:
                location_obj = self.location_repo.upsert(loc_data)
                synced_locations_count += 1

                services_data = self.fetch_services_for_location(location_obj.location_id)
                for svc_data in services_data:
                    try:
                        self.service_repo.upsert(location_obj, svc_data)
                        synced_services_count += 1
                    except Exception as s_exc:
                        logger.error("Failed to upsert service %s for location %s: %s", svc_data.get("id"), location_obj.location_id, s_exc)

            except Exception as l_exc:
                logger.error("Failed to upsert location %s: %s", loc_data.get("id"), l_exc)

        logger.info("Services sync finished. Synced %d locations and %d services.", synced_locations_count, synced_services_count)
        return {
            "locations_synced": synced_locations_count,
            "services_synced": synced_services_count
        }

    def get_services_context(self) -> str:
        """Helper to get formatted services text for LLM context."""
        return self.service_repo.get_formatted_context()

