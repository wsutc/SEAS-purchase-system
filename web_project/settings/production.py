# ruff: noqa: F405

try:
    import sentry_sdk  # type: ignore
    from sentry_sdk.integrations.django import DjangoIntegration  # type: ignore
    from sentry_sdk.integrations.logging import LoggingIntegration  # type: ignore
except ImportError:
    from .base import logging

    logging.warning("`sentry_sdk` not installed")

import os

from .base import *  # noqa: F403
from .base import env

# from sentry_sdk.integrations.redis import RedisIntegration


# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env("DJANGO_SECRET_KEY")
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["wsu.edu"])
RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# DATABASES
# ------------------------------------------------------------------------------
# can't use `env.db` because of sslca requirement
# DATABASES["default"] = env.db("DATABASE_URL")  # noqa F405

# if using postgres
# DATABASES["default"] = {  # noqa: F405
#     "ENGINE": "django.db.backends.postgresql",
#     "NAME": env.str("DB_NAME", default="db_name"),
#     "USER": env.str("DB_USER", default="db_username"),
#     "PASSWORD": env.str("DB_PASSWORD", default="db_password"),
#     "HOST": env.str("DB_HOST", default="localhost"),
#     "PORT": env.str("DB_PORT", default=3306),
#     # "OPTIONS": {
#     #     # "charset": "utf8mb4",
#     #     "ssl": {"ca": env.path("AWS_CERT_PATH", default=None)},
#     # },
# }

# if using mysql
DATABASES["default"] = {
    "ENGINE": "django.db.backends.mysql",
    "NAME": env.str("DB_NAME", default="db_name"),
    "USER": env.str("DB_USER", default="db_username"),
    "PASSWORD": env.str("DB_PASSWORD", default="db_password"),
    "HOST": env.str("DB_HOST", default="localhost"),
    "PORT": env.str("DB_PORT", default=3306),
    "OPTIONS": {
        # "charset": "utf8mb4",
        "ssl": {"ca": env.path("AWS_CERT_PATH", default=None)},
    },
}

# logging.info(f"web_project.settings.production DATABASES: {DATABASES}")  # noqa: F405

# DATABASES["default"]["OPTIONS"]["ssl"]["ca"] = env.path("AWS_CERT_PATH", default=None)
DATABASES["default"]["ATOMIC_REQUESTS"] = True  # noqa F405
DATABASES["default"]["CONN_MAX_AGE"] = env.int("CONN_MAX_AGE", default=60)  # noqa F405

# CACHES
# ------------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("REDIS_URL"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            # Mimicking memcache behavior.
            # https://github.com/jazzband/django-redis#memcached-exceptions-behavior
            "IGNORE_EXCEPTIONS": True,
        },
    },
    # "select2": {
    #     "BACKEND": "django_redis.cache.RedisCache",
    #     "LOCATION": env("REDIS_URL"),
    #     "OPTIONS": {
    #         "CLIENT_CLASS": "django_redis.client.DefaultClient",
    #         "IGNORE_EXCEPTIONS": True,
    #     },
    # },
}

# SELECT2_CACHE_BACKEND = "select2"

# SECURITY
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-proxy-ssl-header
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-ssl-redirect
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-secure
SESSION_COOKIE_SECURE = True
# https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-secure
CSRF_COOKIE_SECURE = True
# https://docs.djangoproject.com/en/dev/topics/security/#ssl-https
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-hsts-seconds
# TODO: set this to 60 seconds first and then to 518400 once you prove the former works  # noqa: TD002, TD003, E501
SECURE_HSTS_SECONDS = 60
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-hsts-include-subdomains
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool(
    "DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS",
    default=True,
)
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-hsts-preload
SECURE_HSTS_PRELOAD = env.bool("DJANGO_SECURE_HSTS_PRELOAD", default=True)
# https://docs.djangoproject.com/en/dev/ref/middleware/#x-content-type-options-nosniff
SECURE_CONTENT_TYPE_NOSNIFF = env.bool(
    "DJANGO_SECURE_CONTENT_TYPE_NOSNIFF",
    default=True,
)

# STORAGES
# ------------------------------------------------------------------------------
# https://django-storages.readthedocs.io/en/latest/#installation
INSTALLED_APPS += ["storages"]  # noqa F405
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
AWS_ACCESS_KEY_ID = env("DJANGO_AWS_ACCESS_KEY_ID")
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
AWS_SECRET_ACCESS_KEY = env("DJANGO_AWS_SECRET_ACCESS_KEY")
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
AWS_STORAGE_BUCKET_NAME = env("DJANGO_AWS_STORAGE_BUCKET_NAME")
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
AWS_QUERYSTRING_AUTH = False
# DO NOT change these unless you know what you're doing.
_AWS_EXPIRY = 60 * 60 * 24 * 7
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": f"max-age={_AWS_EXPIRY}, s-maxage={_AWS_EXPIRY}, must-revalidate",
}
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
AWS_S3_REGION_NAME = env("DJANGO_AWS_S3_REGION_NAME", default=None)
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#cloudfront

aws_s3_domain = (
    AWS_S3_CUSTOM_DOMAIN or f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"  # noqa: F405
)

# STATIC
# ------------------------
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
# STATIC_HOST = env.url("DJANGO_AWS_S3_CUSTOM_DOMAIN", default="")

# STATIC_HOST = f"https://{AWS_S3_CUSTOM_DOMAIN.path}"
# STATIC_URL = STATIC_HOST + "/static/"

# MEDIA
# ------------------------------------------------------------------------------
MEDIA_URL = f"https://{aws_s3_domain}/media/"

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#default-from-email
DEFAULT_FROM_EMAIL = env(
    "DJANGO_DEFAULT_FROM_EMAIL",
    default="JustDrive <noreply@justdrive.wooster.xyz>",
)
# https://docs.djangoproject.com/en/dev/ref/settings/#server-email
SERVER_EMAIL = env("DJANGO_SERVER_EMAIL", default=DEFAULT_FROM_EMAIL)
# https://docs.djangoproject.com/en/dev/ref/settings/#email-subject-prefix
EMAIL_SUBJECT_PREFIX = env(
    "DJANGO_EMAIL_SUBJECT_PREFIX",
    default="[JustDrive]",
)

# ADMIN
# ------------------------------------------------------------------------------
# Django Admin URL regex.
try:
    ADMIN_URL = env.url("DJANGO_ADMIN_URL", default="admin/")
except Exception:
    logging.warning("ADMIN_URL not parseable by `env.url`", exc_info=1)
    ADMIN_URL = env.str("DJANGO_ADMIN_URL", defaults="admin/")

# Anymail
# ------------------------------------------------------------------------------
# https://anymail.readthedocs.io/en/stable/installation/#installing-anymail
INSTALLED_APPS += ["anymail"]  # noqa F405
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
# https://anymail.readthedocs.io/en/stable/installation/#anymail-settings-reference
# https://anymail.readthedocs.io/en/stable/esps/sendinblue/
EMAIL_BACKEND = "anymail.backends.sendinblue.EmailBackend"
ANYMAIL = {
    "SENDINBLUE_API_KEY": env("SENDINBLUE_API_KEY"),
    "SENDINBLUE_API_URL": env(
        "SENDINBLUE_API_URL",
        default="https://api.sendinblue.com/v3/",
    ),
}


# LOGGING
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#logging
# See https://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s "
            "%(process)d %(thread)d %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {"level": "INFO", "handlers": ["console"]},
    "loggers": {
        "django.db.backends": {
            "level": "ERROR",
            "handlers": ["console"],
            "propagate": False,
        },
        # Errors logged by the SDK itself
        "sentry_sdk": {"level": "ERROR", "handlers": ["console"], "propagate": False},
        "django.security.DisallowedHost": {
            "level": "ERROR",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}

# Sentry
# ------------------------------------------------------------------------------
SENTRY_DSN = env("SENTRY_DSN")
SENTRY_LOG_LEVEL = env.int("DJANGO_SENTRY_LOG_LEVEL", logging.INFO)

try:
    sentry_logging = LoggingIntegration(
        level=SENTRY_LOG_LEVEL,  # Capture info and above as breadcrumbs
        event_level=logging.ERROR,  # Send errors as events
    )
    integrations = [sentry_logging, DjangoIntegration()]
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=integrations,
        environment=env("SENTRY_ENVIRONMENT", default="production"),
        traces_sample_rate=env.float("SENTRY_TRACES_SAMPLE_RATE", default=0.0),
        auto_session_tracking=env.bool("SENTRY_AUTO_SESSION_TRACKING", default=True),
    )
except Exception:
    logging.warning("`sentry_sdk` not imported")

# Your stuff...
# ------------------------------------------------------------------------------
