from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse


class LegacyCoreCharacterizationTests(TestCase):
    def test_public_pages_render(self):
        for name in ("landing", "home", "about", "contact"):
            with self.subTest(name=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 200)

    @patch("apps.core.views.send_mail")
    def test_contact_submits_and_redirects(self, send_mail):
        response = self.client.post(
            reverse("contact"),
            {
                "from_name": "Legacy tester",
                "from_email": "legacy@example.com",
                "subject": "Characterization",
                "message": "Checking the original contact flow.",
            },
        )

        self.assertRedirects(response, reverse("contact"))
        send_mail.assert_called_once()
