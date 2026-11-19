from datetime import UTC, datetime
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.management import CommandError, call_command
from django.test import SimpleTestCase, TestCase
from django.utils import timezone

from apps.accounts.models import User
from apps.posts.content_import import clean_text, parse_published_at
from apps.posts.management.commands.seed_editorial import (
    EDITORIAL_POSTS,
    validate_editorial_dataset,
)
from apps.posts.models import Post


class ContentHelperTests(SimpleTestCase):
    def test_clean_text_normalizes_and_strips_valid_text(self):
        self.assertEqual(
            clean_text("  Cafe\u0301\r\nracer  ", field="title"), "Caf\u00e9\nracer"
        )

    def test_clean_text_rejects_empty_control_or_provisional_text(self):
        invalid_values = [
            "",
            "   ",
            None,
            "bad\ufffdtext",
            "bad\x00text",
            "TODO: finish article",
            "Lorem ipsum dolor sit amet.",
        ]
        for value in invalid_values:
            with self.subTest(value=value):
                with self.assertRaises(ValidationError):
                    clean_text(value, field="content")

    def test_parse_published_at_handles_strings_and_datetimes(self):
        aware_dt = datetime(2026, 1, 15, 12, 0, tzinfo=UTC)
        self.assertEqual(parse_published_at(aware_dt), aware_dt)
        self.assertEqual(parse_published_at("2026-01-15T12:00:00+00:00"), aware_dt)

        naive_parsed = parse_published_at("2026-01-15T12:00:00")
        self.assertTrue(timezone.is_aware(naive_parsed))

        for invalid in ("not-a-date", "", None):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValidationError):
                    parse_published_at(invalid)


class ContentImportTests(TestCase):
    def test_seed_editorial_is_idempotent_and_uploads_webp_images(self):
        call_command("seed_editorial")
        call_command("seed_editorial")

        author = User.objects.get(email="editorial-author@example.invalid")
        posts = Post.objects.filter(author=author)
        self.assertFalse(author.is_staff)
        self.assertFalse(author.is_superuser)
        self.assertFalse(author.has_usable_password())
        self.assertEqual(posts.count(), 19)
        self.assertEqual(posts.filter(categories__slug="builds").count(), 9)
        self.assertEqual(posts.filter(categories__slug="guides").count(), 6)
        self.assertEqual(posts.filter(categories__slug="reviews").count(), 4)
        self.assertTrue(
            all(post.featured_image.name.endswith(".webp") for post in posts)
        )
        self.assertTrue(all(post.featured_image_alt for post in posts))
        self.assertSetEqual(
            set(posts.values_list("slug", flat=True)),
            {item["slug"] for item in EDITORIAL_POSTS},
        )
        self.assertIn(
            "source/reviews/review-04.webp", {item["image"] for item in EDITORIAL_POSTS}
        )
        self.assertEqual(
            posts.order_by("-published_at").first().slug,
            "una-lista-de-trabajo-que-si-terminas",
        )

    def test_seed_editorial_sets_build_specs_and_reruns_restore_them(self):
        call_command("seed_editorial")

        post = Post.objects.get(slug="cafe-racer-de-garaje")
        self.assertEqual(post.build_specs["donor"], "1957 Norton ES2")
        self.assertEqual(
            Post.objects.get(slug="frenos-antes-de-potencia").build_specs["donor"],
            "Yamaha SR500",
        )
        self.assertEqual(
            Post.objects.get(slug="checklist-para-salir-el-fin-de-semana").build_specs,
            {},
        )
        image_name = post.featured_image.name

        Post.objects.filter(pk=post.pk).update(build_specs={"donor": "Editada"})
        call_command("seed_editorial")

        post.refresh_from_db()
        self.assertEqual(post.build_specs["donor"], "1957 Norton ES2")
        self.assertEqual(post.featured_image.name, image_name)
        self.assertEqual(Post.objects.filter(slug="cafe-racer-de-garaje").count(), 1)

    def test_seed_editorial_build_specs_are_valid_post_data(self):
        call_command("seed_editorial")

        for post in Post.objects.exclude(build_specs={}):
            with self.subTest(slug=post.slug):
                post.full_clean()
                self.assertTrue(post.categories.filter(slug="builds").exists())

    def test_editorial_validation_rejects_invalid_build_specs(self):
        assets_dir = Path(settings.BASE_DIR) / "assets" / "editorial"
        guide = next(item for item in EDITORIAL_POSTS if item["category"] == "guides")
        reference = next(
            item for item in EDITORIAL_POSTS if item["slug"] == "cafe-racer-de-garaje"
        )
        cases = [
            (
                guide,
                {"build_specs": {"donor": "Honda CB750"}},
                "only allowed on builds",
            ),
            (reference, {"build_specs": {"engine": "750 cc"}}, "Unknown build"),
            (reference, {"build_specs": {"donor": " "}}, "Empty build"),
        ]

        for original, overrides, message in cases:
            with self.subTest(message=message):
                posts = [
                    {**item, **overrides} if item is original else item
                    for item in EDITORIAL_POSTS
                ]
                with self.assertRaisesRegex(CommandError, message):
                    validate_editorial_dataset(assets_dir, posts)

        posts = [
            {key: value for key, value in item.items() if key != "build_specs"}
            if item is reference
            else item
            for item in EDITORIAL_POSTS
        ]
        with self.assertRaisesRegex(CommandError, "Missing build specifications"):
            validate_editorial_dataset(assets_dir, posts)

    def test_seed_editorial_dry_run_validates_without_writing_data(self):
        call_command("seed_editorial", "--dry-run")

        self.assertFalse(
            User.objects.filter(email="editorial-author@example.invalid").exists()
        )
        self.assertFalse(Post.objects.exists())

    def test_seed_editorial_does_not_overwrite_another_authors_post(self):
        foreign_author = User.objects.create_user(
            email="another-editor@example.invalid",
            username="another-editor",
            password="unused-password",
        )
        Post.objects.create(
            slug=EDITORIAL_POSTS[0]["slug"],
            title="Contenido de otro autor",
            excerpt="Resumen de otro autor.",
            content="Contenido que la semilla no debe sobrescribir.",
            author=foreign_author,
            status=Post.Status.PUBLISHED,
            published_at="2026-01-01T12:00:00+00:00",
        )

        with self.assertRaisesRegex(CommandError, "another author"):
            call_command("seed_editorial")

        self.assertEqual(
            Post.objects.get(slug=EDITORIAL_POSTS[0]["slug"]).author,
            foreign_author,
        )

    def test_verify_editorial_baseline_confirms_migration_and_categories(self):
        call_command("verify_editorial_baseline")
