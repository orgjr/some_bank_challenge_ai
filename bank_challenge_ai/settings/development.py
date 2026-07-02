import os

from .base import *  # noqa: F401,F403

ENV = "development"

DEBUG = True

SECRET_KEY = os.getenv("DEV_PROJECT_KEY", "dev-secret-key")

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
