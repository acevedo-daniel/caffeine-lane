from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime

from apps.accounts.models import User
from apps.posts.content_import import import_selected_content
from apps.posts.taxonomy import STRUCTURAL_CATEGORIES, CategorySlug

DEMO_CONTENT = {
    "categories": [category.as_content_dict() for category in STRUCTURAL_CATEGORIES],
    "posts": [
        {
            "slug": "workshop-notes",
            "title": "Workshop Notes",
            "excerpt": "A short, clean demo article for local development.",
            "content": "This demo post exists only to make local development easier.",
            "categories": [CategorySlug.BUILDS],
            "published_at": "2026-01-15T12:00:00+00:00",
        },
        {
            "slug": "weekend-ride-checklist",
            "title": "Weekend Ride Checklist",
            "excerpt": "A compact checklist for a safe ride.",
            "content": "Check tyres, lights, fuel, documents, and weather before leaving.",
            "categories": [CategorySlug.GUIDES],
            "published_at": "2026-01-16T12:00:00+00:00",
        },
        {
            "slug": "city-ride-review",
            "title": "City Ride Review",
            "excerpt": "A concise demo review for an everyday cafe racer ride.",
            "content": "This demo review exists only to make local development easier.",
            "categories": [CategorySlug.REVIEWS],
            "published_at": "2026-01-17T12:00:00+00:00",
        },
    ],
}


class Command(BaseCommand):
    help = "Create a small, idempotent, non-privileged demo dataset."

    def handle(self, *args, **options):
        author, created = User.objects.get_or_create(
            email="demo-author@example.invalid",
            defaults={"username": "demo-author", "display_name": "Demo Author"},
        )
        if created:
            author.set_unusable_password()
            author.save(update_fields=["password"])

        result = import_selected_content(DEMO_CONTENT, author=author)
        self.stdout.write(
            self.style.SUCCESS(
                f"Demo data ready: {result['categories']} categories and {result['posts']} posts."
            )
        )
