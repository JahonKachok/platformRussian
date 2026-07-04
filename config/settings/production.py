import os

from .base import *

DEBUG = False

_allowed_hosts = os.environ.get('DJANGO_ALLOWED_HOSTS')
ALLOWED_HOSTS = (
    _allowed_hosts.split(',') if _allowed_hosts
    else ['lingvocompetence.uz', 'www.lingvocompetence.uz']
)

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

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
