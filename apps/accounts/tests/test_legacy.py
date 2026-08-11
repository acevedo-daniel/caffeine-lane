from unittest.mock import patch

from django.core import mail
from django.db import IntegrityError
from django.templatetags.static import static
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.accounts.models import User


class AccountFlowTests(TestCase):
    def register(self, *, email="new@example.com", username="new_user"):
        response = self.client.post(reverse("register_step1"), {"email": email})
        self.assertRedirects(response, reverse("register_step2"))
        return self.client.post(
            reverse("register_step2"),
            {
                "username": username,
                "display_name": "New Rider",
                "password1": "safe-test-password-123",
                "password2": "safe-test-password-123",
                "has_motorcycle": "true",
            },
        )

    def test_registration_creates_custom_user_and_logs_in(self):
        response = self.register()

        self.assertRedirects(response, reverse("home"))
        user = User.objects.get(email="new@example.com")
        self.assertEqual(user.username, "new_user")
        self.assertEqual(user.display_name, "New Rider")
        self.assertTrue(user.has_motorcycle)
        self.assertEqual(self.client.session["_auth_user_id"], str(user.pk))

    def test_registration_step2_rechecks_an_email_taken_after_step1(self):
        step1 = self.client.post(
            reverse("register_step1"), {"email": "race@example.com"}
        )
        self.assertRedirects(step1, reverse("register_step2"))
        User.objects.create_user(
            email="race@example.com",
            username="existing-rider",
            password="safe-test-password-123",
        )

        response = self.client.post(
            reverse("register_step2"),
            {
                "username": "new-rider",
                "display_name": "New Rider",
                "password1": "safe-test-password-123",
                "password2": "safe-test-password-123",
                "has_motorcycle": "true",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "An account with this email already exists.")
        self.assertFalse(User.objects.filter(username="new-rider").exists())

    def test_registration_step2_handles_an_integrity_error(self):
        self.client.post(reverse("register_step1"), {"email": "race@example.com"})

        with patch(
            "apps.accounts.views.RegistrationStep2Form.save",
            side_effect=IntegrityError,
        ):
            response = self.client.post(
                reverse("register_step2"),
                {
                    "username": "new-rider",
                    "display_name": "New Rider",
                    "password1": "safe-test-password-123",
                    "password2": "safe-test-password-123",
                    "has_motorcycle": "true",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "An account with this email already exists.")

    def test_login_uses_email(self):
        user = User.objects.create_user(
            email="rider@example.com",
            username="rider",
            password="safe-test-password-123",
        )

        response = self.client.post(
            reverse("login"),
            {"username": user.email, "password": "safe-test-password-123"},
        )

        self.assertRedirects(response, reverse("home"))

    def test_logout_only_accepts_post(self):
        user = User.objects.create_user(
            email="rider@example.com",
            username="rider",
            password="safe-test-password-123",
        )
        self.client.force_login(user)

        self.assertEqual(self.client.get(reverse("logout")).status_code, 405)
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("home"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_profile_updates_custom_user(self):
        user = User.objects.create_user(
            email="rider@example.com",
            username="rider",
            password="safe-test-password-123",
        )
        self.client.force_login(user)

        response = self.client.post(
            reverse("profile"),
            {
                "display_name": "Updated Rider",
                "bio": "Ready to ride.",
                "personal_url": "https://example.com",
                "has_motorcycle": "on",
            },
        )

        self.assertRedirects(response, reverse("profile"))
        user.refresh_from_db()
        self.assertEqual(user.display_name, "Updated Rider")
        self.assertTrue(user.has_motorcycle)

    def test_profile_uses_static_default_avatar_when_none_is_uploaded(self):
        user = User.objects.create_user(
            email="rider@example.com",
            username="rider",
            password="safe-test-password-123",
        )

        self.assertEqual(user.avatar_url, static("images/default-avatar.svg"))

    def test_password_reset_sends_email(self):
        User.objects.create_user(
            email="rider@example.com",
            username="rider",
            password="safe-test-password-123",
        )

        response = self.client.post(
            reverse("password_reset"), {"email": "rider@example.com"}
        )

        self.assertRedirects(response, reverse("password_reset_done"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("reset/", mail.outbox[0].body)
        self.assertEqual(mail.outbox[0].alternatives[0].mimetype, "text/html")

    @override_settings(PASSWORD_RESET_ENABLED=False)
    def test_password_reset_demo_does_not_send_email(self):
        User.objects.create_user(
            email="rider@example.com",
            username="rider",
            password="safe-test-password-123",
        )

        response = self.client.post(
            reverse("password_reset"), {"email": "rider@example.com"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Password recovery is unavailable")
        self.assertEqual(len(mail.outbox), 0)

    @override_settings(PASSWORD_RESET_ENABLED=False)
    def test_login_explains_demo_password_reset_limit(self):
        response = self.client.get(reverse("login"))

        self.assertContains(response, "Password recovery is unavailable in this demo")

    def test_password_change_updates_credentials(self):
        user = User.objects.create_user(
            email="rider@example.com",
            username="rider",
            password="safe-test-password-123",
        )
        self.client.force_login(user)

        response = self.client.post(
            reverse("password_change"),
            {
                "old_password": "safe-test-password-123",
                "new_password1": "even-safer-test-password-456",
                "new_password2": "even-safer-test-password-456",
            },
        )

        self.assertRedirects(response, reverse("password_change_done"))
        user.refresh_from_db()
        self.assertTrue(user.check_password("even-safer-test-password-456"))
