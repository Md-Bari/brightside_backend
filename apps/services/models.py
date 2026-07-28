"""
Services and Locations Data Models.
Stores external appointment locations and car wash services.
"""
from django.db import models


class Location(models.Model):
    location_id = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=255)
    timezone = models.CharField(max_length=100, blank=True, null=True)
    address = models.JSONField(default=dict, blank=True)
    business_hours = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "service_locations"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.location_id})"

    @property
    def formatted_address(self) -> str:
        if not self.address:
            return ""
        parts = [
            self.address.get("addressLine1", ""),
            self.address.get("locality", ""),
            self.address.get("administrativeDistrictLevel1", ""),
            self.address.get("postalCode", ""),
            self.address.get("country", "")
        ]
        return ", ".join(p for p in parts if p)


class Service(models.Model):
    service_id = models.CharField(max_length=100)
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name="services"
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    description_html = models.TextField(blank=True)
    variations = models.JSONField(default=list, blank=True)
    images = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "location_services"
        unique_together = ("service_id", "location")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} - {self.location.name}"

    @property
    def starting_price_display(self) -> str:
        """Helper to get human-readable starting price from variations."""
        if not self.variations:
            return "N/A"
        prices = []
        for v in self.variations:
            cents = v.get("priceInCents")
            currency = v.get("currency", "USD")
            if cents is not None:
                dollars = cents / 100.0
                prices.append((dollars, currency))
        if not prices:
            return "N/A"
        min_price, curr = min(prices, key=lambda x: x[0])
        return f"${min_price:.2f} {curr}".strip()
