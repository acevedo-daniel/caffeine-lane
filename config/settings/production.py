import os

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403
from .base import INSTALLED_APPS, MIDDLEWARE, env

SECRET_KEY = env.str("SECRET_KEY")
if SECRET_KEY == "change-me-locally" or SECRET_KEY.startswith("django-insecure-"):
    raise ImproperlyConfigured("SECRET_KEY must be set to a production value.")

DEBUG = False
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured("ALLOWED_HOSTS must contain at least one host.")

CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

if not os.environ.get("CLOUDINARY_URL"):
    raise ImproperlyConfigured("CLOUDINARY_URL is required in production.")

INSTALLED_APPS += ["cloudinary_storage", "cloudinary"]
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
STORAGES = {
    "default": {"BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
}

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "WARNING"},
}
