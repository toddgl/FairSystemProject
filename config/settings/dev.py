# config/settings/dev.py

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

print('In the dev environment')

ALLOWED_HOSTS = [
   'ruru',
    'karearea',
    'localhost',
    '127.0.0.1',
    'lynx-dashing-chamois.ngrok-free.app'
]

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

EMAIL_HOST_USER = 'convener@martinboroughfair.org.nz'

SWDC_FOOD_LICENCE_EMAIL_ADDRESS = 'health@swdc.govt.nz'
CSRF_TRUSTED_ORIGINS = [
    'https://lynx-dashing-chamois.ngrok-free.app',
    'http://ruru:8000',
    "http://127.0.0.1:8000",
    "http://localhost:8000"
]

# Stripe Test settings
STRIPE_PUBLISHABLE_KEY = env('STRIPE_PUBLISHABLE_KEY_TEST')
STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY_TEST')
STRIPE_WEBHOOK_SECRET = env('STRIPE_WEBHOOK_SECRET_TEST')

