# config/settings/test.py

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [
    'mbfairsystem.org',
    '149.28.188.154',
    'localhost',
]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Set that requests over HTTP are redirected to HTTPS.
SECURE_SSL_REDIRECT = False

# Session and CSF configuraton
CSRF_COOKIE_SECURE = True  # Set to True if using HTTPS
SESSION_COOKIE_SECURE = True  # Set to True if using HTTPS
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 8640  # 1 day, adjust as needed

# CSRF_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SAMESITE = 'None'

ANYMAIL = {
    # (exact settings here depend on your ESP...)
    "MAILGUN_API_KEY": env('MAILGUN_API_KEY'),
    "MAILGUN_SENDER_DOMAIN": 'mbfairsystem.org',  # your Mailgun domain, if needed
}

EMAIL_BACKEND = 'anymail.backends.mailgun.EmailBackend'
DEFAULT_FROM_EMAIL = 'convener@martinboroughfair.org.nz'
EMAIL_HOST_USER = 'convener@martinboroughfair.org.nz'

CSRF_TRUSTED_ORIGINS = [
    'https://mbfairsystem.org',
    "http://127.0.0.1",
    "http://localhost"
]

# Stripe Test settings
STRIPE_PUBLISHABLE_KEY = env('STRIPE_PUBLISHABLE_KEY_TEST')
STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY_TEST')
STRIPE_WEBHOOK_SECRET = env('STRIPE_WEBHOOK_SECRET_TEST')


# REDIRECT_DOMAIN = 'http://127.0.0.1:8000'
REDIRECT_DOMAIN = 'https://mbfairsystem.org'