# config/settings/prod.py

from .base import *

import boto3

boto3.setup_default_session(region_name='ap-southeast-2')

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

# ANYMAIL = {
#    # (exact settings here depend on your ESP...)
#    "MAILGUN_API_KEY": env('MAILGUN_API_KEY'),
#    "MAILGUN_SENDER_DOMAIN": 'mbfairsystem.org',  # your Mailgun domain, if needed
#}

# EMAIL_BACKEND = 'anymail.backends.mailgun.EmailBackend'

ANYMAIL = {
    "AMAZON_SES_SESSION_PARAMS": {
        "region_name": "ap-southeast-2",
    },
    "AMAZON_SES_CLIENT_PARAMS": {
    # (exact settings here depend on your ESP...),
    "aws_access_key_id": env('AWS_ACCESS_KEY_ID'),
    "aws_secret_access_key": env('AWS_SECRET_ACCESS_KEY')
    },
}

EMAIL_BACKEND = 'anymail.backends.amazon_ses.EmailBackend'

# EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
# EMAIL_FILE_PATH = '/usr/home/admin/restores/mail'

DEFAULT_FROM_EMAIL = 'convener@martinboroughfair.org.nz'
EMAIL_HOST_USER = 'convener@martinboroughfair.org.nz'

PASSWORD_RESET_TIMEOUT = 259200 # 3 days in seconds

SWDC_FOOD_LICENCE_EMAIL_ADDRESS = 'health@swdc.govt.nz'
CSRF_TRUSTED_ORIGINS = [
    'https://mbfairsystem.org',
    "http://127.0.0.1",
    "http://localhost"
]

# Stripe Production setting
STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = env('STRIPE_WEBHOOK_SECRET')


# REDIRECT_DOMAIN = 'http://127.0.0.1:8000'
REDIRECT_DOMAIN = 'https://mbfairsystem.org'
