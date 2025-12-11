# scam_recovery/settings.py - ADD/UPDATE THESE SETTINGS

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-xw!j7)0c5qbe$yo+dpb6*-g&)p4*ksisp#+8+ke(lidmu#!=et'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'simpleui',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'scam_recovery.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.user_wallet',
                'core.context_processors.user_currency',  # Your existing one
                'core.context_processors.site_settings',   # Add this
                'core.context_processors.social_links', 
            ],
        },
    },
]

WSGI_APPLICATION = 'scam_recovery.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

AUTH_USER_MODEL = 'core.User'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'home'

# Security settings
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# ====================
# EMAIL CONFIGURATION
# ====================

# For Development - Console Backend (prints emails to console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# For Production - SMTP Backend (use one of the options below)
"""
# Option 1: Gmail SMTP
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'  # Use App Password, not regular password
DEFAULT_FROM_EMAIL = 'RecoveryPro <your-email@gmail.com>'

# Option 2: SendGrid
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = 'your-sendgrid-api-key'
DEFAULT_FROM_EMAIL = 'RecoveryPro <noreply@yourdomain.com>'

# Option 3: AWS SES
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'email-smtp.us-east-1.amazonaws.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-aws-access-key-id'
EMAIL_HOST_PASSWORD = 'your-aws-secret-access-key'
DEFAULT_FROM_EMAIL = 'RecoveryPro <noreply@yourdomain.com>'

# Option 4: Mailgun
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'postmaster@yourdomain.com'
EMAIL_HOST_PASSWORD = 'your-mailgun-password'
DEFAULT_FROM_EMAIL = 'RecoveryPro <noreply@yourdomain.com>'
"""

# Default email settings (used in development)
DEFAULT_FROM_EMAIL = 'RecoveryPro <noreply@recoverypro.com>'
SERVER_EMAIL = 'RecoveryPro <noreply@recoverypro.com>'

# Admin email notifications
ADMINS = [
    ('Admin', 'admin@recoverypro.com'),
]

MANAGERS = ADMINS

# ====================
# FILE UPLOAD SETTINGS
# ====================

# Maximum upload size (10MB for KYC documents)
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB

# Allowed file extensions for uploads
ALLOWED_DOCUMENT_EXTENSIONS = ['.pdf', '.jpg', '.jpeg', '.png']
ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png']

# ====================
# CURRENCY SETTINGS
# ====================

# Default currency
DEFAULT_CURRENCY = 'USD'

# Exchange rate API (optional - for real-time conversion)
# You can use: exchangerate-api.com, fixer.io, currencylayer.com
EXCHANGE_RATE_API_KEY = 'your-api-key-here'  # Get free key from exchangerate-api.com
EXCHANGE_RATE_API_URL = 'https://api.exchangerate-api.com/v4/latest/USD'

# ====================
# KYC SETTINGS
# ====================

# KYC verification settings
KYC_REQUIRED_FOR_WITHDRAWAL = True
KYC_REQUIRED_FOR_CASE_SUBMISSION = False
KYC_MAX_RESUBMISSIONS = 3

# ====================
# PASSWORD RESET SETTINGS
# ====================

# Password reset token expiry (in hours)
PASSWORD_RESET_TIMEOUT = 24

# ====================
# LOGGING CONFIGURATION
# ====================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'email_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'emails.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'core.email': {
            'handlers': ['email_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Create logs directory if it doesn't exist
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)


CSRF_TRUSTED_ORIGINS = [
    "https://recovery-bxrp.onrender.com",
]
