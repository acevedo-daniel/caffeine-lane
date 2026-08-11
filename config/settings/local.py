from .base import *  # noqa: F403
from .base import BASE_DIR, DATABASES, INSTALLED_APPS, MIDDLEWARE, STORAGES, env

# The local settings module is exclusively for development. Keeping this
# explicit ensures runserver serves the compiled static assets on Windows even
# when a machine-level DEBUG variable is set to false.
DEBUG = True
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])
CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS", default=["http://localhost:8000"]
)

DATABASES["default"] = env.db(
    "DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"
)
DATABASES["default"]["CONN_MAX_AGE"] = 0

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Uploaded media remains on the local filesystem during development.
STORAGES["default"] = {"BACKEND": "django.core.files.storage.FileSystemStorage"}

INSTALLED_APPS += ["debug_toolbar"]
MIDDLEWARE.insert(1, "debug_toolbar.middleware.DebugToolbarMiddleware")
INTERNAL_IPS = ["127.0.0.1"]
