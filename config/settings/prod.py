# config/settings/prod.py

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

print('Production environment')
ANYMAIL = {
    # (exact settings here depend on your ESP...)
    "MAILGUN_API_KEY": env('MAILGUN_API_KEY'),
    "MAILGUN_SENDER_DOMAIN": 'mbfairsystem.org',  # your Mailgun domain, if needed
}

EMAIL_BACKEND = 'anymail.backends.mailgun.EmailBackend'
DEFAULT_FROM_EMAIL = 'convener@martinboroughfair.org.nz'
EMAIL_HOST_USER = 'convener@martinboroughfair.org.nz'

SWDC_FOOD_LICENCE_EMAIL_ADDRESS = 'health@swdc.govt.nz'
CSRF_TRUSTED_ORIGINS = [
    'https://mbfairsystem.org',
    "http://127.0.0.1",
    "http://localhost"
]

# Stripe Production setting
STRIPE_PUBLISHABLE_KEY = env('STRIPE_PUBLISHABLE_KEY')
STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = env('STRIPE_WEBHOOK_SECRET')