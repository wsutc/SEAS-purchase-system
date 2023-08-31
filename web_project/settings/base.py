"""
Django settings for web_project project.

Generated by 'django-admin startproject' using Django 4.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

import logging
from pathlib import Path
from socket import gethostname

import environ
from django.contrib.messages import constants as message_constants

from web_project.helpers import plog

env = environ.Env(DEBUG=(bool, False))

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

DEV_MACHINES = ["tc-metech-5080", "wtsmain-m01", "wtsmain-linux"]

hostname = gethostname()
if hostname.lower() in DEV_MACHINES:
    print(f"Current hostname: {hostname}")
    READ_DOT_ENV_FILE = True
else:
    READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", default=False)
if READ_DOT_ENV_FILE:
    env_file = Path(BASE_DIR, ".env")
    if env_file.is_file():
        env.read_env(env_file)

APPS_DIR = Path(BASE_DIR / "web_project")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str(
    "DJANGO_SECRET_KEY",
    default="django-insecure-=575&#l3pkg&6i%bmymmf+o@7$)tj8oxd=tvsn(n^0!3d8n013",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DJANGO_DEBUG", False)
TEMPLATE_DEBUG = env.bool("DJANGO_TEMPLATE_DEBUG", False)

logger = logging.getLogger()

if DEBUG:
    logger.setLevel(logging.DEBUG)
    # logging.basicConfig(level="DEBUG")
    log_kwargs = {
        "logger": logger,
        "path": "web_project.settings",
        "level": logging.DEBUG,
    }
    MESSAGE_LEVEL = message_constants.DEBUG
    import mimetypes

    js_path = "/toolbar.js"
    old_js = mimetypes.guess_type(js_path, True)
    logging.debug(f"Old js type: {old_js}")

    mimetypes.add_type("text/javascript", ".js", True)

    new_js = mimetypes.guess_type(js_path, True)
    logging.debug(f"New js type: {new_js}")
else:
    log_kwargs = {
        "logger": logger,
        "path": "web_project.settings",
        "level": logging.DEBUG,
    }
    MESSAGE_LEVEL = message_constants.WARNING

plog(text="last 4 of secret key", value=SECRET_KEY[-4:], **log_kwargs)
plog(text="Current hostname", value=hostname, **log_kwargs)

DEBUG_TOOLBAR_CONFIG = {
    "DISABLE_PANELS": {
        # 'debug_toolbar.panels.history.HistoryPanel',
        # 'debug_toolbar.panels.versions.VersionsPanel',
        # 'debug_toolbar.panels.timer.TimerPanel',
        "debug_toolbar.panels.settings.SettingsPanel",
        "debug_toolbar.panels.headers.HeadersPanel",
        "debug_toolbar.panels.request.RequestPanel",
        "debug_toolbar.panels.sql.SQLPanel",
        "debug_toolbar.panels.staticfiles.StaticFilesPanel",
        "debug_toolbar.panels.templates.TemplatesPanel",
        "debug_toolbar.panels.cache.CachePanel",
        "debug_toolbar.panels.signals.SignalsPanel",
        "debug_toolbar.panels.redirects.RedirectsPanel",
        # 'debug_toolbar.panels.profiling.ProfilingPanel',
    },
}

# Application definition

# CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'

_DJANGO_APPS = [
    "whitenoise.runserver_nostatic",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

_THIRD_PARTY_APPS = [
    # "silk",
    # "constance",
    "bootstrap_datepicker_plus",
    "crispy_bootstrap5",
    "crispy_forms",
    "django_gravatar",
    "django_listview_filters",
    "phonenumber_field",
    "debug_toolbar",
    "djmoney",
    "django_select2",
    "modelclone",
    "widget_tweaks",
    # "constance.backends.database",
]

_LOCAL_APPS = [
    "accounts",
    # "assets",
    "globals",
    "inventory",
    "partnumbers",
    "purchases",
    "setup_sheets",
    "tool_compatibility",
    "users",
]

INSTALLED_APPS = _DJANGO_APPS + _THIRD_PARTY_APPS + _LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # "silk.middleware.SilkyMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # "login_required.middleware.LoginRequiredMiddleware",
    "web_project.helpers.LoginRequiredMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # "django_cprofile_middleware.middleware.ProfilerMiddleware",
]

ROOT_URLCONF = "web_project.urls"


# TEMPLATES
# -----------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [Path(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # 'purchases.views.manufacturers',
                # 'purchases.views.states',
            ],
        },
    },
]

# FORM_RENDERER = "django.forms.renderers.TemplateSetting"

WSGI_APPLICATION = "web_project.wsgi.application"


# MEDIA
# --------------------------------------------------------------------------------------
MEDIA_ROOT = Path(BASE_DIR, "media")
MEDIA_URL = "/media/"


# Database
# --------------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": Path(BASE_DIR, "db.sqlite3"),
    },
}

# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": "redis://127.0.0.1:6379/2",
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient",
#             "IGNORE_EXCEPTIONS": True,
#         },
#     },
#     # "select2": {
#     #     "BACKEND": "django_redis.cache.RedisCache",
#     #     "LOCATION": "redis://127.0.0.1:6379/2",
#     #     "OPTIONS": {
#     #         "CLIENT_CLASS": "django_redis.client.DefaultClient",
#     #     },
#     # },
# }

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.mysql",
#         "NAME": env.str("DB_NAME", default="db_name"),
#         "USER": env.str("DB_USER", default="db_username"),
#         "PASSWORD": env.str("DB_PASSWORD", default="db_password"),
#         "HOST": env.str("DB_HOST", default="localhost"),
#         "PORT": env.str("DB_PORT", default=3306),
#         "OPTIONS": {
#             "charset": "utf8mb4",
#             "ssl": {"ca": env.path("AWS_CERT_PATH", default="")},
#         },
#         "TEST": {"CHARSET": "utf8mb4", "COLLATION": "utf8mb4_unicode_ci"},
#     },
# }

# print(f"databases.default: {DATABASES}")

# AUTHENTICATION
# --------------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend"]
AUTH_USER_MODEL = "users.User"
LOGIN_REDIRECT_URL = "/"
# LOGIN_URL = "account_login"

# PASSWORDS
# --------------------------------------------------------------------------------

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.ScryptPasswordHasher",
]

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",  # noqa: 501
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


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"

# TIME_ZONE = 'UTC'
TIME_ZONE = "America/Los_Angeles"

USE_I18N = True

USE_TZ = True

# STATIC
# ----------------------------------------------------------------------------

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/
AWS_S3_CUSTOM_DOMAIN = env.url("DJANGO_AWS_S3_CUSTOM_DOMAIN", default=None)

plog(text="aws_s3_custom_domain", value=AWS_S3_CUSTOM_DOMAIN, **log_kwargs)

if AWS_S3_CUSTOM_DOMAIN:
    AWS_S3_CUSTOM_DOMAIN = AWS_S3_CUSTOM_DOMAIN.path
    STATIC_HOST = f"https://{AWS_S3_CUSTOM_DOMAIN}"
else:
    STATIC_HOST = ""


# STATIC_HOST = env.url("DJANGO_AWS_S3_CUSTOM_DOMAIN", default="")
# STATIC_HOST = f"https://{AWS_S3_CUSTOM_DOMAIN}" if AWS_S3_CUSTOM_DOMAIN else ""
STATIC_URL = f"{STATIC_HOST}/static/"
STATIC_ROOT = Path(BASE_DIR, "staticfiles")
STATICFILES_DIRS = [
    Path(BASE_DIR, "static/"),
]
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

plog(text="Static Host", value=STATIC_HOST, **log_kwargs)

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

INTERNAL_IPS = ("127.0.0.1",)


# EMAIL
# -----------------------------------------------------------------------------
EMAIL_BACKEND = env(
    "DJANGO_EMAIL_BACKEND",
    default="django.core.mail.backends.smtp.EmailBackend",
)

EMAIL_TIMEOUT = 5


# ADMINS
# -------------------------------------------------------------------------------
# ADMIN_URL = "admin/"


# LOGGING
# -----------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "formatters": {
        "django.server": {
            "()": "django.utils.log.ServerFormatter",
            "format": "[{server_time}] {levelname} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} `{module}` {message}",
            "style": "{",
        },
        # "verbose": {
        #     "format": "{levelname} {asctime} {module} "
        #     "{process} {thread} {message}"
        #     # "format": "%(levelname)s %(asctime)s %(module)s "
        #     # "%(process)d %(thread)d %(message)s"
        # },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "django.server": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "django.server",
        },
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
    },
    "loggers": {
        # "purchases": {
        #     "handlers": ["console"],
        #     "level": "INFO",
        # },
        "django": {
            "handlers": ["console", "mail_admins"],
            "level": "INFO",
            "propagate": False,
        },
        "django.server": {
            "handlers": ["django.server"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"],
    },
}


# THIRD-PARTY
# -------------------------------------------------------------------
PHONENUMBER_DEFAULT_REGION = "US"
PHONENUMBER_DEFAULT_FORMAT = "NATIONAL"

FILTERVIEW_SHOW_UNUSED_FILTERS = False
FILTERVIEW_SHOW_ALL = False

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

GRAVATAR_DEFAULT_IMAGE = "retro"
GRAVATAR_DEFAULT_RATING = "g"

CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"
# SILKY_AUTHORISATION = True
# SILKY_META = True
# SILKY_PYTHON_PROFILER = env.bool("SILKY_PYTHON_PROFILER", default="False")

CONSTANCE_CONFIG = {
    # "SILKY_PYTHON_PROFILER": (
    #     False,
    #     "Whether to run the Silk Profiler.",
    #     bool,
    # ),
    # "SILKY_INTERCEPT_PERCENT": (
    #     100,
    #     (
    #         "What percent of requests to log; set to 0 to prevent Silk from "
    #         "collecting any data."
    #     ),
    #     int,
    # ),
    # "SILKY_META": (
    #     False,
    #     "Whether to show the effect of Slik on the request.",
    #     bool,
    # ),
    # "SILKY_PYTHON_PROFILER_BINARY": (
    #     False,
    #     "Generate binary .prof file.",
    #     bool,
    # ),
}

# CUSTOM
# -------------------------------------------------------------------

PYTRACK_17TRACK_KEY = env.str("PYTRACK_17TRACK_KEY", default="!!!MISSING API KEY!!!")

MESSAGE_TAGS = {
    message_constants.SUCCESS: "alert alert-success",
    message_constants.ERROR: "alert alert-danger",
    message_constants.WARNING: "alert alert-warning",
    message_constants.INFO: "alert alert-info",
    message_constants.DEBUG: "alert alert-secondary",
}

TRACKER_PARAMS = [
    "trackingnumber",
    "tracking_number",
    "strorigtracknum",
]

ALLOWED_ANONYMOUS_VIEWS = [
    "LoginView",
    "LogoutView",
    "PasswordResetView",
]

TRACKER_WEBHOOK_URL = env.str("DJANGO_TRACKER_WEBHOOK_URL", default="")
