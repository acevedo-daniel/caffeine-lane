import io
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from apps.accounts.models import User
from apps.tests.factories import (
    CategoryFactory,
    CommentFactory,
    PostFactory,
    UserFactory,
)


def create_test_image(format="PNG", size=(100, 100), color="blue"):
    file_obj = io.BytesIO()
    image = Image.new("RGB", size, color=color)
    image.save(file_obj, format=format)
    file_obj.seek(0)
    return SimpleUploadedFile(
        f"test.{format.lower()}",
        file_obj.read(),
        content_type=f"image/{format.lower()}",
    )


class Phase6AccountTests(TestCase):
    def setUp(self):
        self.user = UserFactory(
            username="phase6rider", email="phase6@example.com", has_motorcycle=True
        )
        self.category = CategoryFactory(name="Builds")
        self.post = PostFactory(title="Norton Commando Build", categories=self.category)

    def test_registration_flow_step1_to_step2_with_avatar_and_motorcycle(self):
        # Step 1: Submit email
        step1_response = self.client.post(
            reverse("register_step1"), {"email": "newrider@example.com"}
        )
        self.assertRedirects(step1_response, reverse("register_step2"))
        self.assertEqual(
            self.client.session.get("registration_email"), "newrider@example.com"
        )

        # Step 2: Submit profile details with avatar upload
        avatar = create_test_image(format="PNG")
        step2_response = self.client.post(
            reverse("register_step2"),
            {
                "username": "caferacer99",
                "display_name": "Racer 99",
                "password1": "SecurePass123!",
                "password2": "SecurePass123!",
                "has_motorcycle": "true",
                "avatar": avatar,
            },
        )
        self.assertRedirects(step2_response, reverse("home"))

        # Verify user record created with avatar and motorcycle status
        created_user = User.objects.get(email="newrider@example.com")
        self.assertEqual(created_user.username, "caferacer99")
        self.assertEqual(created_user.display_name, "Racer 99")
        self.assertTrue(created_user.has_motorcycle)
        self.assertTrue(bool(created_user.avatar))
        self.assertTrue(created_user.avatar.name.startswith("avatars/"))

    @patch("apps.core.image_validators.MAX_IMAGE_BYTES", 100)
    def test_avatar_upload_rejects_oversized_files(self):
        self.client.force_login(self.user)
        # Create a valid JPEG whose actual byte size exceeds the patched MAX_IMAGE_BYTES
        huge_file = create_test_image(format="JPEG")

        response = self.client.post(
            reverse("profile"),
            {
                "display_name": "Rider",
                "bio": "Garage life",
                "has_motorcycle": "on",
                "avatar": huge_file,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Images must be 5 MB or smaller.")

    def test_avatar_upload_rejects_unsupported_format(self):
        self.client.force_login(self.user)
        # GIF is a valid image format but not allowed (only JPEG, PNG, WEBP)
        gif_file = create_test_image(format="GIF")

        response = self.client.post(
            reverse("profile"),
            {
                "display_name": "Rider",
                "bio": "Garage life",
                "has_motorcycle": "on",
                "avatar": gif_file,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "Images must use one of these formats: JPEG, PNG, WEBP."
        )

    def test_profile_hub_displays_fleet_overview_and_recent_comments(self):
        self.client.force_login(self.user)

        # Create two comments on a post
        c1 = CommentFactory(
            author=self.user,
            post=self.post,
            content="Great valve adjustment guide!",
        )
        c2 = CommentFactory(
            author=self.user,
            post=self.post,
            content="What torque spec did you use on the cylinder head?",
        )

        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)

        # Avatar management & preview card
        self.assertContains(response, "profile-avatar-card")
        self.assertContains(response, "Avatar Management")

        # Motorcycle fleet card
        self.assertContains(response, "profile-fleet-card")
        self.assertContains(response, "Active Garage Rider")

        # Recent comments history section
        self.assertContains(response, "profile-comments-section")
        self.assertContains(response, "Norton Commando Build")
        self.assertContains(response, c1.content)
        self.assertContains(response, c2.content)
        self.assertContains(
            response, reverse("comment_edit", kwargs={"comment_id": c1.id})
        )

    def test_profile_hub_fleet_card_shows_enthusiast_when_no_motorcycle(self):
        enthusiast = UserFactory(
            username="dreamer", email="dreamer@example.com", has_motorcycle=False
        )
        self.client.force_login(enthusiast)

        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enthusiast & Project Builder")
        self.assertContains(response, "No comments posted yet")

    def test_simulated_error_pages_render_rider_oops_in_xl_bezel(self):
        for status_code, url, kicker in [
            (400, "/400/", "400 · Request misfire"),
            (403, "/403/", "403 · Access restricted"),
            (404, "/404/", "404 · Page not found"),
            (500, "/500/", "500 · Server error"),
        ]:
            with self.subTest(status_code=status_code):
                response = self.client.get(url)
                self.assertEqual(response.status_code, status_code)
                self.assertContains(
                    response, "character-oops.webp", status_code=status_code
                )
                self.assertContains(
                    response, "character-badge--xl", status_code=status_code
                )
                self.assertContains(response, kicker, status_code=status_code)

    @override_settings(DEBUG=False)
    def test_production_404_renders_oops_layout(self):
        response = self.client.get("/a-totally-nonexistent-url-slug/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "character-oops.webp", status_code=404)
        self.assertContains(response, "character-badge--xl", status_code=404)
        self.assertContains(response, "Wrong turn.", status_code=404)
        self.assertContains(response, reverse("search"), status_code=404)
