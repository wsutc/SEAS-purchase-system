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

SILKY_PYTHON_PROFILER = True
SILKY_PYTHON_PROFILER_BINARY = True
SILKY_DYNAMIC_PROFILING = [
    # {
    #     "module": "django.utils.deprecation",
    #     "function": "MiddlewareMixin.__call__",
    # },
    {
        "module": "django.core.handlers.exception",
        "function": "convert_exception_to_response",
    },
    {
        "module": "django.core.handlers.exception",
        "function": "get_exception_response",
        "name": "get_exception_response",
    },
    {
        "module": "django.shortcuts",
        "function": "render",
        "name": "django.shortcuts.render",
    },
    # {
    # "module": "django.core.handlers.base",
    # "function": "BaseHandler.get_response",
    # },
    {
        "module": "web_project.helpers",
        "function": "LoginRequiredMiddleware.process_view",
    },
    # {
    #     "module": "django.core.handlers.exception",
    #     "function": "convert_exception_to_response.inner",
    # },
    # {
    #     "module": "web_project.helpers",
    #     "function": "LoginRequiredMiddleware.__call__",
    # },
]

DEBUG_PROPAGATE_EXCEPTIONS = True
