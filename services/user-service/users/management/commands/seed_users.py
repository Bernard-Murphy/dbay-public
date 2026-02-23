"""Create 100 seed users with deterministic IDs and usernames (shared with listing-service seed)."""
from django.core.management.base import BaseCommand
from users.models import User
from users.seed_constants import SEED_USER_IDS, SEED_USERNAMES


class Command(BaseCommand):
    help = "Create 100 seed users. First user gets is_staff=True."

    def handle(self, *args, **options):
        created = 0
        for i, (uid, username) in enumerate(zip(SEED_USER_IDS, SEED_USERNAMES)):
            _, was_created = User.objects.get_or_create(
                id=uid,
                defaults={
                    "username": username,
                    "email": f"{username}@example.com",
                    "display_name": username,
                    "cognito_sub": f"seed-{uid[:8]}",
                    "is_staff": i == 0,
                },
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f"Seed users: {created} created, {100 - created} already existed."))
