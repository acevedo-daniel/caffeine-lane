from .base import *  # noqa: F403
from .base import BASE_DIR, DATABASES, INSTALLED_APPS, MIDDLEWARE, env

DEBUG = env.bool("DEBUG", default=True)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])
CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS", default=["http://localhost:8000"]
)

DATABASES["default"] = env.db(
    "DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"
)
DATABASES["default"]["CONN_MAX_AGE"] = 0

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

INSTALLED_APPS += ["debug_toolbar"]
MIDDLEWARE.insert(1, "debug_toolbar.middleware.DebugToolbarMiddleware")
INTERNAL_IPS = ["127.0.0.1"]
