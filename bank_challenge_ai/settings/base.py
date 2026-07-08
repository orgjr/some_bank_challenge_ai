import os
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ["SECRET_KEY"]

# health check
START_TIME = time.time()

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    # Local
    "account",
    "business",
    "core",
    "person",
    "transaction",
    "user",
    "drf_spectacular",
    "drf_spectacular_sidecar",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "bank_challenge_ai.urls"

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

WSGI_APPLICATION = "bank_challenge_ai.wsgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Digital Banking API Challenge",
    "DESCRIPTION": "This project is a backend coding challenge simulating a digital banking system. It implements core banking features such as account creation, transfers, transaction history, authorization flow, and notification processing. Built with Django and Django REST Framework, it demonstrates REST API design, service-oriented architecture, and transactional consistency.",
    "VERSION": "0.9.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
    "TAGS": [
        {
            "name": "Index",
            "description": "General API information, version, and available endpoints.",
        },
        {
            "name": "Health",
            "description": "System health check and monitoring endpoint.",
        },
        {
            "name": "Login",
            "description": "Session-based user authentication.",
        },
        {
            "name": "Logout",
            "description": "Session termination for authenticated users.",
        },
        {
            "name": "Accounts",
            "description": "Bank account management — creation, retrieval, and listing of accounts.",
        },
        {
            "name": "Business",
            "description": "CRUD operations for business user profiles.",
        },
        {
            "name": "Persons",
            "description": "CRUD operations for person (individual) user profiles.",
        },
        {
            "name": "Transfers",
            "description": "Money transfers between accounts and transaction history.",
        },
        {
            "name": "Users",
            "description": "Authenticated user profile retrieval.",
        },
    ],
    "CONTACT": {
        "name": "Osmar Garcia",
        "email": "osmar.rgj@gmail.com",
        "url": "https://github.com/orgjr",
    },
    "LICENSE": {"name": "MIT"},
}

LANGUAGE_CODE = "en-us"

TIME_ZONE = "America/Sao_Paulo"

USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "user.UserModel"
