from datetime import timedelta
from pathlib import Path

try:
    from decouple import config as config  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    import os

    def config(key, default=None, cast=str):
        value = os.getenv(key)
        if value is None or value == "":
            value = default

        if cast is None:
            return value

        if cast is bool:
            if isinstance(value, bool):
                return value
            if value is None:
                return False
            return str(value).strip().lower() in {"1", "true", "t", "yes", "y", "on"}

        return cast(value) if value is not None else value

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# base.py lives at config/settings/base.py, so we go up 3 levels to project root.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# Application definition

INSTALLED_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # drf
    "rest_framework",
    "django_filters",
    # auth
    "rest_framework.authtoken",
    "dj_rest_auth",
    "corsheaders",
    # utils
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "django_cleanup.apps.CleanupConfig",
    "drf_standardized_errors",
    # 📦 apps
    "apps.core",
    "apps.user",
    "apps.product",
    "apps.inventory",
    "apps.crm",
    "apps.area",
    "apps.sales",
    "apps.finance",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Django REST Framework / Auth

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "dj_rest_auth.jwt_auth.JWTCookieAuthentication",
    ),
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "DEFAULT_SCHEMA_CLASS": "drf_standardized_errors.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "drf_standardized_errors.handler.exception_handler",
}

REST_AUTH = {
    "USE_JWT": True,
    "JWT_AUTH_HTTPONLY": False,
}


# CSRF Configuration

CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default="",
    cast=lambda v: [s.strip() for s in v.split(",") if s.strip()],
)


# Internationalization

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"


# Media files (User uploaded files)

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"


# Default primary key field type

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Spectacular

SPECTACULAR_SETTINGS = {
    "TITLE": "KAS | API Documentation",
    "DESCRIPTION": "API description",
    "VERSION": "1.0.2",
    "SERVE_INCLUDE_SCHEMA": False,
    "CAMELIZE_NAMES": True,
    "POSTPROCESSING_HOOKS": [],
    "COMPONENT_SPLIT_REQUEST": True,
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "#",
    "REDOC_DIST": "SIDECAR",
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "defaultModelsExpandDepth": -1,
        "persistAuthorization": True,
        "tagsSorter": "alpha",
        "operationsSorter": "alpha",
    },
}


def jwt_settings(access_lifetime: timedelta, signing_key: str) -> dict:
    return {
        "ACCESS_TOKEN_LIFETIME": access_lifetime,
        "REFRESH_TOKEN_LIFETIME": timedelta(days=365),
        "ROTATE_REFRESH_TOKENS": False,
        "BLACKLIST_AFTER_ROTATION": False,
        "UPDATE_LAST_LOGIN": False,
        "ALGORITHM": "HS256",
        "SIGNING_KEY": signing_key,
        "VERIFYING_KEY": None,
        "AUDIENCE": None,
        "ISSUER": None,
        "JWK_URL": None,
        "LEEWAY": 0,
        "AUTH_HEADER_TYPES": ("Bearer",),
        "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
        "USER_ID_FIELD": "id",
        "USER_ID_CLAIM": "user_id",
        "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
        "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
        "TOKEN_TYPE_CLAIM": "token_type",
        "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
        "JTI_CLAIM": "jti",
        "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
        "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
        "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
    }

