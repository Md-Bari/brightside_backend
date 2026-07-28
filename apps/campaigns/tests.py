from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Campaign


class CampaignsTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create campaigns
        self.active_campaign = Campaign.objects.create(
            title="Summer Shine Splash",
            description="Get $5 off on Ultimate Glow",
            is_active=True,
        )
        self.inactive_campaign = Campaign.objects.create(
            title="Expired Campaign",
            description="This campaign is expired",
            is_active=False,
        )

    def test_campaign_scheduling_bounds(self):
        from django.utils import timezone
        from datetime import timedelta

        now = timezone.now()

        # 1. Future campaign (start_date in future) - should be inactive
        future_campaign = Campaign.objects.create(
            title="Future Campaign",
            description="Starts tomorrow",
            is_active=True,
            start_date=now + timedelta(days=1),
        )

        # 2. Expired campaign (end_date in past) - should be inactive
        expired_campaign = Campaign.objects.create(
            title="Past Campaign",
            description="Ended yesterday",
            is_active=True,
            end_date=now - timedelta(days=1),
        )

        # 3. Scheduled active campaign (start_date in past, end_date in future) - should be active
        scheduled_active = Campaign.objects.create(
            title="Scheduled Active",
            description="Active now",
            is_active=True,
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=1),
        )

        # Get active campaigns list
        active_list = Campaign.objects.active()

        self.assertIn(self.active_campaign, active_list)
        self.assertNotIn(self.inactive_campaign, active_list)
        self.assertNotIn(future_campaign, active_list)
        self.assertNotIn(expired_campaign, active_list)
        self.assertIn(scheduled_active, active_list)

    def test_session_creation_returns_campaigns(self):
        # Creating a session should return active campaigns
        response = self.client.post(
            "/api/v1/sessions/",
            {"email": "customer@example.com"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        campaigns = response.data["data"]["campaigns"]
        self.assertEqual(len(campaigns), 1)
        self.assertEqual(campaigns[0]["title"], "Summer Shine Splash")

    def test_admin_list_campaigns(self):
        # Admin endpoint can view all campaigns
        response = self.client.get("/api/v1/admin/campaigns/")
        self.assertEqual(response.status_code, 200)
        data = response.data["data"]
        self.assertEqual(len(data), 2)

    def test_admin_create_campaign_with_image(self):
        # Admin endpoint can create a campaign with image
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04"
            b"\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02"
            b"\x02\x4c\x01\x00\x3b"
        )
        uploaded_image = SimpleUploadedFile(
            name="test_image.gif", content=small_gif, content_type="image/gif"
        )

        response = self.client.post(
            "/api/v1/admin/campaigns/",
            {
                "title": "Winter Truck Week",
                "description": "Trucks are washed at car price",
                "image": uploaded_image,
                "is_active": True,
            },
            format="multipart",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["data"], {})
        campaign = Campaign.objects.get(title="Winter Truck Week")
        self.assertEqual(campaign.description, "Trucks are washed at car price")
        self.assertTrue("test_image" in campaign.image.name)

    def test_admin_delete_campaign(self):
        # Admin endpoint can delete a campaign
        response = self.client.delete(
            f"/api/v1/admin/campaigns/{self.inactive_campaign.id}/"
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Campaign.objects.filter(id=self.inactive_campaign.id).exists())

    def test_anonymous_can_crud(self):
        # Anonymous users can perform CRUD on admin endpoints
        response = self.client.get("/api/v1/admin/campaigns/")
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            "/api/v1/admin/campaigns/",
            {"title": "Anonymous Camp", "description": "No auth needed"},
            format="multipart",
        )
        self.assertEqual(response.status_code, 201)
