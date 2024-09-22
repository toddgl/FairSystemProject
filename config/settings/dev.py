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

# Session and CSF configuraton
CSRF_COOKIE_SECURE = False  # Set to True if using HTTPS
SESSION_COOKIE_SECURE = False  # Set to True if using HTTPS
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 8640  # 1 day, adjust as needed

# CSRF_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SAMESITE = 'Lax'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

EMAIL_HOST_USER = 'convener@martinboroughfair.org.nz'

SWDC_FOOD_LICENCE_EMAIL_ADDRESS = 'g.todd@internet.co.nz'

CSRF_TRUSTED_ORIGINS = [
    'http://lynx-dashing-chamois.ngrok-free.app',
    'http://ruru:8000',
    "http://127.0.0.1:8000",
    "http://localhost:8000"
]

# Stripe Test settings
STRIPE_PUBLISHABLE_KEY = env('STRIPE_PUBLISHABLE_KEY_TEST')
STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY_TEST')
STRIPE_WEBHOOK_SECRET = env('STRIPE_WEBHOOK_SECRET_TEST')

REDIRECT_DOMAIN = 'http://127.0.0.1:8000'
# REDIRECT_DOMAIN = 'https://lynx-dashing-chamois.ngrok-free.app'

