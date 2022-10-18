from .base import *  # noqa: F40
from .base import env

# GENERAL
# --------------------------------------------------------
# DEBUG = True

# SECRET_KEY = env.str(
#     "DJANGO_SECRET_KEY",
#     default=SECRET_KEY,  # noqa: F405
# )
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["127.0.0.1"])

_LOCAL_APPS = [
    # "django_mysql",
]

INSTALLED_APPS += _LOCAL_APPS  # noqa: F405
