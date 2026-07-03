from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

# Dev email
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
