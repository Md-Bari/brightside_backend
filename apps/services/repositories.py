"""
Repository layer for Location and Service ORM operations.
Only Repositories touch the ORM directly.
"""
from typing import List, Optional
from django.db import transaction
from .models import Location, Service


class LocationRepository:
    def upsert(self, data: dict) -> Location:
        loc_id = data.get("id")
        if not loc_id:
            raise ValueError("Location data missing 'id'")

        location, _ = Location.objects.update_or_create(
            location_id=loc_id,
            defaults={
                "name": data.get("name", ""),
                "timezone": data.get("timezone", ""),
                "address": data.get("address", {}),
                "business_hours": data.get("businessHours", {}),
            }
        )
        return location

    def list_all(self) -> List[Location]:
        return list(Location.objects.all())

    def get_by_id(self, location_id: str) -> Optional[Location]:
        return Location.objects.filter(location_id=location_id).first()


class ServiceRepository:
    def upsert(self, location: Location, data: dict) -> Service:
        service_id = data.get("id")
        if not service_id:
            raise ValueError("Service data missing 'id'")

        service, _ = Service.objects.update_or_create(
            service_id=service_id,
            location=location,
            defaults={
                "name": data.get("name", ""),
                "description": data.get("description", ""),
                "description_html": data.get("descriptionHtml", ""),
                "variations": data.get("variations", []),
                "images": data.get("images", []),
            }
        )
        return service

    def list_by_location(self, location_id: str) -> List[Service]:
        return list(Service.objects.filter(location__location_id=location_id).select_related("location"))

    def list_all(self) -> List[Service]:
        return list(Service.objects.all().select_related("location"))

    def get_formatted_context(self) -> str:
        """
        Builds a comprehensive text summary of all active locations and services
        to inject into the LLM system prompt context.
        """
        locations = Location.objects.all().prefetch_related("services")
        if not locations.exists():
            return "No service or location information is currently available in the system."

        context_parts = []
        for loc in locations:
            address_str = loc.formatted_address or "Address not specified"
            loc_block = [
                f"### LOCATION: {loc.name} (Location ID: {loc.location_id})",
                f"Address: {address_str}",
                f"Timezone: {loc.timezone or 'N/A'}",
            ]
            
            services = loc.services.all()
            if not services.exists():
                loc_block.append("No services currently listed for this location.")
            else:
                loc_block.append("Available Services:")
                for svc in services:
                    vars_info = []
                    for v in svc.variations:
                        v_name = v.get("name", "Regular")
                        dur = v.get("durationMinutes")
                        cents = v.get("priceInCents")
                        dur_str = f"{dur} mins" if dur else "N/A"
                        price_str = f"${cents/100:.2f}" if cents is not None else "N/A"
                        vars_info.append(f"{v_name}: {price_str} (Duration: {dur_str})")

                    vars_summary = "; ".join(vars_info) if vars_info else "Pricing details upon request"
                    clean_desc = svc.description.replace("\n", " ").strip() if svc.description else "No detailed description."
                    
                    loc_block.append(
                        f"  - Service Name: {svc.name}\n"
                        f"    Service ID: {svc.service_id}\n"
                        f"    Pricing & Variations: {vars_summary}\n"
                        f"    Description: {clean_desc}"
                    )

            context_parts.append("\n".join(loc_block))

        return "\n\n".join(context_parts)
