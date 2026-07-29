import json
import tempfile
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase

from apps.accounts.models import User
from apps.posts.content_import import import_selected_content
from apps.posts.models import Category, Post


class ContentImportTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            email="editor@example.com", username="editor", password="test-password"
        )
        self.payload = {
            "categories": [{"slug": "guides", "name": "Guides"}],
            "posts": [
                {
                    "slug": "clean-import",
                    "title": "Clean Import",
                    "excerpt": "A reviewed import excerpt.",
                    "content": "A reviewed import body.",
                    "categories": ["guides"],
                    "published_at": "2026-01-15T12:00:00+00:00",
                }
            ],
        }

    def test_seed_demo_is_idempotent_and_creates_no_privileged_user(self):
        call_command("seed_demo")
        call_command("seed_demo")

        author = User.objects.get(email="demo-author@example.invalid")
        self.assertFalse(author.is_staff)
        self.assertFalse(author.is_superuser)
        self.assertFalse(author.has_usable_password())
        self.assertEqual(Post.objects.filter(author=author).count(), 3)
        self.assertEqual(
            Category.objects.filter(slug__in=["builds", "guides", "reviews"]).count(),
            3,
        )

    def test_selected_import_is_idempotent(self):
        import_selected_content(self.payload, author=self.author)
        import_selected_content(self.payload, author=self.author)

        post = Post.objects.get(slug="clean-import")
        self.assertEqual(Post.objects.filter(slug="clean-import").count(), 1)
        self.assertEqual(post.status, Post.Status.PUBLISHED)
        self.assertEqual(
            list(post.categories.values_list("slug", flat=True)), ["guides"]
        )

    def test_selected_import_rejects_privileged_users_and_provisional_text(self):
        self.author.is_staff = True
        self.author.save(update_fields=["is_staff"])
        with self.assertRaises(ValidationError):
            import_selected_content(self.payload, author=self.author)

    def test_selected_import_rejects_image_fields(self):
        self.payload["posts"][0]["featured_image"] = "posts/media/unreviewed.jpg"

        with self.assertRaises(ValidationError):
            import_selected_content(self.payload, author=self.author)

    def test_selected_import_rejects_reserved_post_slugs(self):
        self.payload["posts"][0]["slug"] = "search"

        with self.assertRaises(ValidationError):
            import_selected_content(self.payload, author=self.author)

        self.author.is_staff = False
        self.author.save(update_fields=["is_staff"])
        self.payload["posts"][0]["content"] = "TODO: review this."
        with self.assertRaises(ValidationError):
            import_selected_content(self.payload, author=self.author)

    def test_management_command_reads_utf8_json(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", encoding="utf-8", delete=False
        ) as file:
            json.dump(self.payload, file)
            path = Path(file.name)
        self.addCleanup(path.unlink)

        call_command(
            "import_selected_content", path, "--author-email", self.author.email
        )

        self.assertTrue(Post.objects.filter(slug="clean-import").exists())
