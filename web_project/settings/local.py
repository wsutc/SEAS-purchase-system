from .base import *  # noqa: F40
from .base import env

# GENERAL
# --------------------------------------------------------
DEBUG = True

SECRET_KEY = env.str(
    "DJANGO_SECRET_KEY",
    default="!!!SET DJANGO_SECRET_KEY!!!",
)
# ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default="127.0.0.1")

INSTALLED_APPS += "debug_toolbar"  # noqa: F405
