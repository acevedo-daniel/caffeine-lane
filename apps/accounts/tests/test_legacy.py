from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import Profile


class LegacyAccountsCharacterizationTests(TestCase):
    def test_registration_two_step_creates_user_and_profile(self):
        step_one = self.client.post(
            reverse("register_step1"), {"email": "new@example.com"}
        )
        self.assertRedirects(step_one, reverse("register_step2"))

        step_two = self.client.post(
            reverse("register_step2"),
            {
                "username": "legacy_new_user",
                "first_name": "Legacy",
                "last_name": "User",
                "password1": "safe-test-password-123",
                "password2": "safe-test-password-123",
                "gender": "O",
                "has_moto": "True",
            },
        )

        self.assertRedirects(step_two, reverse("home"))
        user = User.objects.get(username="legacy_new_user")
        self.assertEqual(user.email, "new@example.com")
        self.assertFalse(Profile.objects.get(user=user).has_moto)

    def test_profile_requires_authentication(self):
        response = self.client.get(reverse("profile"))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('profile')}")

    def test_password_reset_page_is_available(self):
        response = self.client.get(reverse("password_reset"))
        self.assertEqual(response.status_code, 200)
