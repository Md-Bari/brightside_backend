from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.core.management import call_command

from apps.services.models import Location, Service
from apps.services.repositories import LocationRepository, ServiceRepository
from apps.services.services import ServiceSyncService


class ServicesModelAndRepositoryTest(TestCase):
    def setUp(self):
        self.loc_repo = LocationRepository()
        self.svc_repo = ServiceRepository()

    def test_location_and_service_creation(self):
        loc_data = {
            "id": "LOC_TEST_101",
            "name": "Brightside Main Wash",
            "timezone": "America/New_York",
            "address": {
                "addressLine1": "123 Main St",
                "locality": "Springfield",
                "administrativeDistrictLevel1": "IL",
                "postalCode": "62701",
                "country": "US"
            },
            "businessHours": {"periods": []}
        }
        loc = self.loc_repo.upsert(loc_data)
        self.assertEqual(loc.location_id, "LOC_TEST_101")
        self.assertEqual(loc.formatted_address, "123 Main St, Springfield, IL, 62701, US")

        svc_data = {
            "id": "SVC_TEST_201",
            "name": "Express Exterior Wash",
            "description": "Quick 15-min exterior wash and shine.",
            "descriptionHtml": "<p>Quick 15-min exterior wash and shine.</p>",
            "variations": [
                {"id": "VAR_1", "name": "Regular", "durationMinutes": 15, "priceInCents": 2500, "currency": "USD"}
            ],
            "images": ["https://example.com/wash.jpg"]
        }
        svc = self.svc_repo.upsert(loc, svc_data)
        self.assertEqual(svc.service_id, "SVC_TEST_201")
        self.assertEqual(svc.location, loc)
        self.assertEqual(svc.starting_price_display, "$25.00 USD")

        formatted_context = self.svc_repo.get_formatted_context()
        self.assertIn("LOC_TEST_101", formatted_context)
        self.assertIn("Express Exterior Wash", formatted_context)
        self.assertIn("$25.00", formatted_context)


class ServiceSyncServiceTest(TestCase):
    @patch.object(ServiceSyncService, "_http_get_json")
    def test_sync_all(self, mock_http_get):
        mock_http_get.side_effect = [
            # Locations API response
            {
                "success": True,
                "data": [
                    {
                        "id": "LOC_MOCK_1",
                        "name": "Mock Location",
                        "timezone": "UTC",
                        "address": {"addressLine1": "100 Mock Ave"},
                        "businessHours": {}
                    }
                ]
            },
            # Services API response
            {
                "success": True,
                "data": [
                    {
                        "id": "SVC_MOCK_1",
                        "name": "Mock Full Detail",
                        "description": "Complete full detail package.",
                        "variations": [{"name": "Regular", "durationMinutes": 60, "priceInCents": 10000}]
                    }
                ]
            }
        ]

        sync_service = ServiceSyncService(base_url="https://mock-api.test")
        result = sync_service.sync_all()

        self.assertEqual(result["locations_synced"], 1)
        self.assertEqual(result["services_synced"], 1)
        self.assertEqual(Location.objects.count(), 1)
        self.assertEqual(Service.objects.count(), 1)


class SyncServicesCommandTest(TestCase):
    @patch.object(ServiceSyncService, "sync_all")
    def test_management_command(self, mock_sync):
        mock_sync.return_value = {"locations_synced": 2, "services_synced": 5}
        call_command("sync_services")
        mock_sync.assert_called_once()
