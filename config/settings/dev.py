from datetime import timedelta

from .base import *  # noqa: F403

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY", default="unsafe-dev-secret-key")

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="localhost,127.0.0.1,[::1]",
    cast=lambda v: [s.strip() for s in v.split(",") if s.strip()],
)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    }
}

# CORS
CORS_ORIGIN_ALLOW_ALL = config("CORS_ORIGIN_ALLOW_ALL", default=True, cast=bool)
if not CORS_ORIGIN_ALLOW_ALL:
    CORS_ALLOWED_ORIGINS = config(
        "CORS_ALLOWED_ORIGINS",
        default="",
        cast=lambda v: [s.strip() for s in v.split(",") if s.strip()],
    )

SIMPLE_JWT = jwt_settings(access_lifetime=timedelta(days=1), signing_key=SECRET_KEY)  # noqa: F405

