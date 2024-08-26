# config/settings/test.py

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

print('In the test environment')

CSRF_TRUSTED_ORIGINS = [
    'https://mbfairsystem.org',
    "http://127.0.0.1",
    "http://localhost"
]

# Stripe Test settings
STRIPE_PUBLISHABLE_KEY = env('STRIPE_PUBLISHABLE_KEY_TEST')
STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY_TEST')
STRIPE_WEBHOOK_SECRET = env('STRIPE_WEBHOOK_SECRET_TEST')

