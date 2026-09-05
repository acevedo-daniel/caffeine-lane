from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.db.migrations.recorder import MigrationRecorder

from apps.posts.models import Category
from apps.posts.taxonomy import STRUCTURAL_CATEGORIES


class Command(BaseCommand):
    help = "Verify the structural post taxonomy required by the deployed site."

    def handle(self, *args, **options):
        migration_is_applied = (
            MigrationRecorder(connection)
            .migration_qs.filter(app="posts", name="0007_create_structural_categories")
            .exists()
        )
        if not migration_is_applied:
            raise CommandError(
                "posts.0007_create_structural_categories is not applied. Run migrate first."
            )

        expected_slugs = {category.slug for category in STRUCTURAL_CATEGORIES}
        existing_slugs = set(
            Category.objects.filter(slug__in=expected_slugs).values_list(
                "slug", flat=True
            )
        )
        missing_slugs = sorted(expected_slugs - existing_slugs)
        if missing_slugs:
            raise CommandError(
                "Missing structural categories: " + ", ".join(missing_slugs)
            )

        self.stdout.write(
            self.style.SUCCESS("Structural taxonomy verified: builds, guides, reviews.")
        )
