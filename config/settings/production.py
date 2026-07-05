import os

from django.core.exceptions import ImproperlyConfigured

from .base import *

DEBUG = False

# The dev fallback in base.py must never be used in production.
if SECRET_KEY == 'django-insecure-rustili-platform-change-in-production-xyz123':
    raise ImproperlyConfigured(
        'Set the DJANGO_SECRET_KEY environment variable before running with '
        'config.settings.production.'
    )

_allowed_hosts = os.environ.get('DJANGO_ALLOWED_HOSTS')
ALLOWED_HOSTS = (
    _allowed_hosts.split(',') if _allowed_hosts
    else ['lingvocompetence.uz', 'www.lingvocompetence.uz']
)

_csrf_trusted_origins = os.environ.get('DJANGO_CSRF_TRUSTED_ORIGINS')
CSRF_TRUSTED_ORIGINS = (
    _csrf_trusted_origins.split(',') if _csrf_trusted_origins
    else ['https://lingvocompetence.uz', 'https://www.lingvocompetence.uz']
)

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Only trust the X-Forwarded-Proto header when actually sitting behind a
# reverse proxy/load balancer that terminates TLS and sets it itself —
# otherwise a client could spoof "https" and defeat SECURE_SSL_REDIRECT.
if os.environ.get('DJANGO_BEHIND_PROXY', '').lower() in ('1', 'true', 'yes'):
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SECURE_HSTS_SECONDS = int(os.environ.get('DJANGO_HSTS_SECONDS', 60 * 60 * 24 * 7))
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Serve pre-compressed, cache-busted static files directly via WhiteNoise
# without needing a separate nginx/CDN static file server.
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': BASE_DIR / 'cache',
    }
}

# Error notifications
ADMINS = [
    tuple(pair.split(':', 1))
    for pair in os.environ.get('DJANGO_ADMINS', '').split(',')
    if ':' in pair
]
MANAGERS = ADMINS
SERVER_EMAIL = os.environ.get('DJANGO_SERVER_EMAIL', DEFAULT_FROM_EMAIL)

# SMTP in production if configured, otherwise fall back to the console
# backend inherited from base.py so the site still runs without mail set up.
if os.environ.get('EMAIL_HOST'):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ['EMAIL_HOST']
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
    EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'true').lower() in ('1', 'true', 'yes')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{asctime} {levelname} {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django.request': {
            'handlers': ['console', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}
