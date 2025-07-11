import environ
from django.conf.locale.en import formats as en_formats
from pathlib import Path
import os
from django.urls import reverse_lazy

# Base directory using pathlib.Path
BASE_DIR = Path(__file__).resolve().parent.parent

# Environment setup
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR / '.env')

# Security settings
SECRET_KEY = env('SECRET_KEY')
DEBUG = env.bool('DEBUG', default=False)

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'snorthoneurocare.com', 'www.snorthoneurocare.com', '103.199.215.103', '192.168.0.114']

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = [
    'https://snorthoneurocare.com',
    'https://www.snorthoneurocare.com',
    'http://103.199.215.103:8000',
    'https://103.199.215.103:8000',
    'http://127.0.0.1',
    'http://localhost',
    'http://192.168.0.114:8001'
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.humanize',
    "django_htmx",
    'widget_tweaks',
    'crispy_forms',
    'django_filters',
    'crispy_bootstrap5',
    'django_crontab',
    "phonenumber_field",
    'import_export',
    'sweetify',
    'patient',
    'event',
    'web',
    'doctor',
    'user',
    'diagnostics',
    'medications',
    'inventory',
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "django_htmx.middleware.HtmxMiddleware",
    'healthcare.middleware.TimezoneMiddleware',
    'healthcare.middleware.RedirectWWWToNonWWWMiddleware',
    'healthcare.middleware.CurrentOrgMiddleware',
    'healthcare.middleware.AutoAttendanceMiddleware',
]

ROOT_URLCONF = 'healthcare.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'user.context_processor.org',
                'user.context_processor.branches',
                'user.context_processor.site',
            ],
        },
    },
]

WSGI_APPLICATION = 'healthcare.wsgi.application'

AUTHENTICATION_BACKENDS = [
    'user.authentication.CustomAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
]

DATABASES = {
    'default': {
        'ENGINE': env.str('DB_ENGINE', default='django.db.backends.postgresql'),
        'NAME': env.str('DB_NAME'),
        'HOST': env.str('DB_HOST', default='localhost'),
        'PORT': env.int('DB_PORT', default=5432),
        'USER': env.str('DB_USER'),
        'PASSWORD': env.str('DB_PASSWORD'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Date and Time formats
en_formats.DATE_FORMAT = 'd/m/Y'
en_formats.TIME_FORMAT = 'h:i A'

# Static & Media
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'require_debug_false': {'()': 'django.utils.log.RequireDebugFalse'},
        'require_debug_true': {'()': 'django.utils.log.RequireDebugTrue'},
    },
    'formatters': {
        'django.server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[{server_time}] {message}',
            'style': '{',
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        },
        'django.server': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'django.server',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django': {'handlers': ['console', 'mail_admins'], 'level': 'INFO'},
        'django.server': {'handlers': ['django.server'], 'level': 'INFO', 'propagate': False},
    }
}

# Authentication & Sessions
AUTH_USER_MODEL = "user.User"
LOGIN_REDIRECT_URL = '/user/?order_date=today'
LOGOUT_REDIRECT_URL = reverse_lazy('user:login')
LOGIN_URL = reverse_lazy('user:login')

APPEND_SLASH = False
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Twilio (if required)
TWILIO_SID = env('TWILIO_SID')
TWILIO_AUTH_TOKEN = env('TWILIO_AUTH_TOKEN')
TWILIO_MES_SID = env('TWILIO_MES_SID')

SITE_ID = 1
