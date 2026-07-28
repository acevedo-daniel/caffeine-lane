from unittest.mock import patch

from django.template.loader import get_template
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


class ErrorPageTests(TestCase):
    def test_custom_error_templates_are_available(self):
        for template_name in ("400.html", "403.html", "404.html", "500.html"):
            with self.subTest(template_name=template_name):
                self.assertIsNotNone(get_template(template_name))

    def test_missing_page_uses_custom_404_template(self):
        response = self.client.get("/page-that-does-not-exist/")

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")
