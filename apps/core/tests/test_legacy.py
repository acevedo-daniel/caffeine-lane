from unittest.mock import patch

from anymail.exceptions import AnymailAPIError
from django.core import mail
from django.core.cache import cache
from django.template.loader import get_template
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse
from django.utils.csp import CSP


class LegacyCoreCharacterizationTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_public_pages_render(self):
        for name in ("landing", "home", "about", "contact"):
            with self.subTest(name=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 200)

    def test_health_endpoint_is_available_without_database_queries(self):
        with self.assertNumQueries(0):
            response = self.client.get(reverse("healthz"))

        self.assertEqual(response.json(), {"status": "ok"})

    def test_base_layout_uses_compiled_assets_not_tailwind_play_cdn(self):
        response = self.client.get(reverse("home"))

        self.assertContains(response, "dist/css/app.css")
        self.assertContains(response, "dist/js/base.js")
        self.assertNotContains(response, "cdn.tailwindcss.com")

    def test_contact_sends_text_and_html_email_with_reply_to(self):
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
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.reply_to, ["legacy@example.com"])
        self.assertIn("Checking the original contact flow.", email.body)
        self.assertEqual(email.alternatives[0].mimetype, "text/html")

    def test_contact_rejects_honeypot_and_rate_limits_messages(self):
        payload = {
            "from_name": "Legacy tester",
            "from_email": "legacy@example.com",
            "subject": "Characterization",
            "message": "Checking the contact flow.",
        }
        spam_response = self.client.post(
            reverse("contact"), {**payload, "website": "x"}
        )

        self.assertEqual(spam_response.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)

        for _ in range(5):
            response = self.client.post(reverse("contact"), payload)
            self.assertEqual(response.status_code, 302)
        limited_response = self.client.post(reverse("contact"), payload)

        self.assertEqual(limited_response.status_code, 200)
        self.assertContains(limited_response, "Too many messages")
        self.assertEqual(len(mail.outbox), 5)

    def test_contact_handles_email_delivery_failures_without_reporting_success(self):
        payload = {
            "from_name": "Legacy tester",
            "from_email": "legacy@example.com",
            "subject": "Characterization",
            "message": "Checking delivery failure handling.",
        }

        with (
            patch(
                "apps.core.views.EmailMultiAlternatives.send",
                side_effect=AnymailAPIError("delivery failed"),
            ),
            self.assertLogs("apps.core.views", level="WARNING") as logs,
        ):
            response = self.client.post(reverse("contact"), payload)

        self.assertEqual(response.status_code, 503)
        self.assertContains(response, "We could not send your message", status_code=503)
        self.assertNotContains(response, "Thank you for your message", status_code=503)
        self.assertIn("error_type=AnymailAPIError", logs.output[0])


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
