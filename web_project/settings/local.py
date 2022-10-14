from .base import *  # noqa: F40
from .base import _17TRACK_KEY, env  # noqa: F40

# GENERAL
# --------------------------------------------------------
DEBUG = True

SECRET_KEY = env.str(
    "DJANGO_SECRET_KEY",
    default="!!!SET DJANGO_SECRET_KEY!!!",
)
# ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default="127.0.0.1")

_LOCAL_APPS = [
    "debug_toolbar",
    "django_mysql",
]

INSTALLED_APPS += _LOCAL_APPS  # noqa: F405
