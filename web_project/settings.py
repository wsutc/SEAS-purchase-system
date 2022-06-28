"""
Django settings for web_project project.

Generated by 'django-admin startproject' using Django 4.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

import environ
import os
from pathlib import Path

env = environ.Env(
    DEBUG=(bool, False)
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

print(os.path.join(BASE_DIR, '.env'))

environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-=575&#l3pkg&6i%bmymmf+o@7$)tj8oxd=tvsn(n^0!3d8n013'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1','d4e0-69-166-40-1.ngrok.io']


# Application definition

# CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'

INSTALLED_APPS = [
    # 'constance.backends.database',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'phonenumber_field',
    'djmoney',
    'widget_tweaks',
    'purchases',
    'setup_sheets',
    'inventory',
    'django_mysql',
    'bootstrap_modal_forms',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'web_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # 'purchases.views.manufacturers',
                # 'purchases.views.states',
            ],
        },
    },
]

WSGI_APPLICATION = 'web_project.wsgi.application'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': BASE_DIR / 'db.sqlite3',
    # }
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT'),
        'CHARSET': 'utf8mb4',
        'COLLATION': 'utf8mb4_unicode_ci'
    },
    "TEST": {
        "CHARSET": "utf8mb4",
        "COLLATION": 'utf8mb4_unicode_ci'
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

# TIME_ZONE = 'UTC'
TIME_ZONE = 'America/Los_Angeles'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

INTERNAL_IPS = (
    '127.0.0.1',
)

PHONENUMBER_DEFAULT_REGION = 'US'

PHONENUMBER_DEFAULT_FORMAT = 'NATIONAL'

# Custom settings

DEFAULT_TAX_RATE = '.086'
DEFAULT_INSTRUCTIONS = 'Because grand total amount does not include shipping/handling and tax costs, Dr. Mo approves if total costs exceeds grand total amount.'

# Constance

# CONSTANCE_CONFIG = {
#     'DEFAULT_TAX_RATE': ('.086','Default Sales Tax Rate (8.6 is entered as .086'),
#     'DEFAULT_INSTRUCTIONS': ('Because grand total amount does not include shipping/handling and tax costs, Dr. Mo approves if total costs exceeds grand total amount.','Default "Instructions" on Purchase Requests')
# }

LOGIN_REDIRECT_URL = '/'


# EASYPOST_KEY = env('EASYPOST_KEY')
AFTERSHIP_KEY = env('AFTERSHIP_KEY')
AFTERSHIP_WEBHOOK_SECRET = env('AFTERSHIP_WEBHOOK_SECRET')
SHIP24_KEY = env('SHIP24_KEY')
SHIP24_WEBHOOK_SECRET = env('SHIP24_WEBHOOK_SECRET')

SMARTSHEET_SHEET_NAME = env('SMARTSHEET_SHEET_NAME')

_17TRACK_KEY = env('_17TRACK_KEY')