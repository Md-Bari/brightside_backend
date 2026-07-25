from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.sessions.models import ChatSession
from apps.users.models import CustomerUser


class Command(BaseCommand):
    help = "Seeds demo users and chat sessions for development and testing."

    def handle(self, *args, **options):
        self.stdout.write("Deleting existing user and session data...")
        ChatSession.objects.all().delete()
        CustomerUser.objects.all().delete()

        self.stdout.write("Seeding demo customer users...")

        # User 1: Alice Vance
        alice = CustomerUser.objects.create(
            email="alice.vance@example.com",
            name="Alice Vance",
        )
        # Session 1: Alice Vance (Ended)
        ChatSession.objects.create(
            user=alice,
            status=ChatSession.Status.ENDED,
            messages=[
                {"role": "user", "content": "Hi, what are the current promotions?"},
                {
                    "role": "assistant",
                    "content": "Hi Alice! We currently have our 'Summer Shine Splash' campaign running. You can get $5 off on our Ultimate Glow wash!",
                },
                {"role": "user", "content": "Great! Thanks."},
                {
                    "role": "assistant",
                    "content": "You're welcome! Let me know if you need anything else.",
                },
            ],
            ended_at=timezone.now(),
        )

        # Session 2: Alice Vance (Active)
        ChatSession.objects.create(
            user=alice,
            status=ChatSession.Status.ACTIVE,
            messages=[
                {"role": "user", "content": "Hello, what are your opening hours?"},
                {
                    "role": "assistant",
                    "content": "Hi Alice! We are open from 8:00 AM to 8:00 PM, Monday through Sunday.",
                },
            ],
        )

        # User 2: Bob Smith
        bob = CustomerUser.objects.create(
            email="bob.smith@example.com",
            name="Bob Smith",
        )
        # Session 3: Bob Smith (Active)
        ChatSession.objects.create(
            user=bob,
            status=ChatSession.Status.ACTIVE,
            messages=[
                {"role": "user", "content": "Do you wash large trucks?"},
                {
                    "role": "assistant",
                    "content": "Hi Bob! Yes, we wash trucks. We currently have a 'Winter Truck Week' campaign starting soon.",
                },
            ],
        )

        # User 3: Charlie Brown (No sessions)
        CustomerUser.objects.create(
            email="charlie.brown@example.com",
            name="Charlie Brown",
        )

        self.stdout.write(
            self.style.SUCCESS("Successfully seeded demo users and sessions!")
        )
