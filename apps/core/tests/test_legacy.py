from unittest.mock import patch

from django.template.loader import get_template
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse
from django.utils.csp import CSP


class LegacyCoreCharacterizationTests(TestCase):
    def test_public_pages_render(self):
        for name in ("landing", "home", "about", "contact"):
            with self.subTest(name=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 200)

    def test_base_layout_uses_compiled_assets_not_tailwind_play_cdn(self):
        response = self.client.get(reverse("home"))

        self.assertContains(response, "dist/css/app.css")
        self.assertContains(response, "dist/js/base.js")
        self.assertNotContains(response, "cdn.tailwindcss.com")

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


class ContentSecurityPolicyTests(TestCase):
    @override_settings(
        MIDDLEWARE=[
            "django.middleware.security.SecurityMiddleware",
            "django.middleware.csp.ContentSecurityPolicyMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
        ],
        SECURE_CSP_REPORT_ONLY={
            "default-src": [CSP.SELF],
            "script-src": [CSP.SELF],
        },
    )
    def test_report_only_policy_uses_native_django_middleware(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(
            response["Content-Security-Policy-Report-Only"],
            "default-src 'self'; script-src 'self'",
        )
        self.assertNotIn("Content-Security-Policy", response)

    def test_csp_report_endpoint_logs_browser_reports(self):
        response = self.client.post(
            reverse("csp_report"),
            data='{"csp-report": {"violated-directive": "script-src"}}',
            content_type="application/csp-report",
        )

        self.assertEqual(response.status_code, 204)
