import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[3]
SRC_DIR = BASE_DIR / "src"


def get_env(name: str, default: str | None = None) -> str | None:
    return os.getenv(name, default)


def get_bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


SECRET_KEY = get_env("DJANGO_SECRET_KEY", "unsafe-dev-secret-key")
DEBUG = get_bool_env("DJANGO_DEBUG", False)

ALLOWED_HOSTS = [
    host.strip()
    for host in get_env("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")
    if host.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "group_finance.apps.core",
    "group_finance.apps.org",
    "group_finance.apps.people",
    "group_finance.apps.imports",
    "group_finance.apps.banking",
    "group_finance.apps.worklog",
    "group_finance.apps.payroll",
    "group_finance.apps.expenses",
    "group_finance.apps.revenue",
    "group_finance.apps.analytics",
    "group_finance.apps.reports",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "group_finance.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "group_finance.wsgi.application"
ASGI_APPLICATION = "group_finance.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": get_env("POSTGRES_DB", "group_finance"),
        "USER": get_env("POSTGRES_USER", "group_finance"),
        "PASSWORD": get_env("POSTGRES_PASSWORD", "group_finance"),
        "HOST": get_env("POSTGRES_HOST", "localhost"),
        "PORT": get_env("POSTGRES_PORT", "5432"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "Asia/Almaty"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"] if (BASE_DIR / "static").exists() else []

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

