import os
import subprocess
import sys
from pathlib import Path

from django.test import SimpleTestCase


class ProductionSettingsTests(SimpleTestCase):
    def test_documented_resend_environment_loads_production_settings(self):
        environment = os.environ.copy()
        for name in (
            "EMAIL_HOST",
            "EMAIL_PORT",
            "EMAIL_HOST_USER",
            "EMAIL_HOST_PASSWORD",
            "EMAIL_USE_TLS",
            "EMAIL_TIMEOUT",
        ):
            environment.pop(name, None)
        environment.update(
            {
                "DJANGO_SETTINGS_MODULE": "config.settings.production",
                "SECRET_KEY": "test-production-secret-key-not-for-deployment-0123456789",
                "DATABASE_URL": "sqlite:///:memory:",
                "ALLOWED_HOSTS": "example.test",
                "CSRF_TRUSTED_ORIGINS": "https://example.test",
                "CLOUDINARY_URL": "cloudinary://123456789012345:test@example",
                "RESEND_API_KEY": "re_test_not_a_real_key",
                "DEFAULT_FROM_EMAIL": "The Caffeine Lane <onboarding@resend.dev>",
                "CONTACT_RECIPIENT_EMAIL": "owner@example.test",
                "USE_X_FORWARDED_PROTO": "true",
                "CSP_ENFORCE": "false",
                "SECURE_HSTS_SECONDS": "3600",
                "SECURE_HSTS_INCLUDE_SUBDOMAINS": "false",
                "SECURE_HSTS_PRELOAD": "false",
            }
        )
        result = subprocess.run(
            [
                sys.executable,
                "manage.py",
                "check",
                "--settings=config.settings.production",
            ],
            cwd=Path(__file__).resolve().parents[3],
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_production_settings_require_database_url(self):
        environment = os.environ.copy()
        environment.update(
            {
                "DJANGO_SETTINGS_MODULE": "config.settings.production",
                "SECRET_KEY": "test-production-secret-key-not-for-deployment-0123456789",
                "DATABASE_URL": "",
            }
        )
        result = subprocess.run(
            [
                sys.executable,
                "manage.py",
                "check",
                "--settings=config.settings.production",
            ],
            cwd=Path(__file__).resolve().parents[3],
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("DATABASE_URL is required in production.", result.stderr)

    def test_documented_production_backends_are_enabled_with_debug_disabled(self):
        environment = os.environ.copy()
        environment.update(
            {
                "DJANGO_SETTINGS_MODULE": "config.settings.production",
                "SECRET_KEY": "test-production-secret-key-not-for-deployment-0123456789",
                "DATABASE_URL": "sqlite:///:memory:",
                "ALLOWED_HOSTS": "example.test",
                "CLOUDINARY_URL": "cloudinary://123456789012345:test@example",
                "RESEND_API_KEY": "re_test_not_a_real_key",
                "CONTACT_RECIPIENT_EMAIL": "owner@example.test",
            }
        )
        result = subprocess.run(
            [
                sys.executable,
                "manage.py",
                "shell",
                "--settings=config.settings.production",
                "-c",
                (
                    "from django.conf import settings; "
                    "print(settings.DEBUG); "
                    "print(settings.EMAIL_BACKEND); "
                    "print(settings.STORAGES['default']['BACKEND']); "
                    "print(settings.STORAGES['staticfiles']['BACKEND'])"
                ),
            ],
            cwd=Path(__file__).resolve().parents[3],
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(
            [line for line in result.stdout.splitlines() if line][-4:],
            [
                "False",
                "anymail.backends.resend.EmailBackend",
                "cloudinary_storage.storage.MediaCloudinaryStorage",
                "whitenoise.storage.CompressedManifestStaticFilesStorage",
            ],
        )


class LocalSettingsTests(SimpleTestCase):
    def test_local_settings_are_explicitly_development_oriented(self):
        environment = os.environ.copy()
        environment.update(
            {
                "DJANGO_SETTINGS_MODULE": "config.settings.local",
                "DEBUG": "false",
                "DATABASE_URL": "sqlite:///:memory:",
            }
        )
        result = subprocess.run(
            [
                sys.executable,
                "manage.py",
                "shell",
                "--settings=config.settings.local",
                "-c",
                (
                    "from django.conf import settings; "
                    "print(settings.DEBUG); "
                    "print(settings.EMAIL_BACKEND); "
                    "print(settings.STORAGES['default']['BACKEND'])"
                ),
            ],
            cwd=Path(__file__).resolve().parents[3],
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(
            [line for line in result.stdout.splitlines() if line][-3:],
            [
                "True",
                "django.core.mail.backends.console.EmailBackend",
                "django.core.files.storage.FileSystemStorage",
            ],
        )
