# Production settings for deployment
from .settings import *
import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Add your domain/server IP to ALLOWED_HOSTS
ALLOWED_HOSTS = [
    'emmanalhedad.pythonanywhere.com',
    'your-domain.com',  # Replace with your actual domain
    'localhost',
    '127.0.0.1',
]

# Database configuration for production
# You might want to use PostgreSQL or MySQL in production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Static files configuration for production
STATIC_ROOT = '/home/emmanalhedad/student-server-django/staticfiles'  # Adjust for your server
MEDIA_ROOT = '/home/emmanalhedad/student-server-django/media'  # Adjust for your server

# Security settings for production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# CORS settings for production
CORS_ALLOW_ALL_ORIGINS = False  # Set to False in production
CORS_ALLOWED_ORIGINS = [
    "https://emmanalhedad.pythonanywhere.com",
    # Add your frontend domains here
]

# Logging configuration for production
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': '/home/emmanalhedad/student-server-django/django.log',  # Adjust path
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}