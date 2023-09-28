import os

from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(f'{BASE_DIR}/.env')

# Quick-start development settings - unsuitable for production
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('IS_DEBUG', False) == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')
CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # third party apps
    'rest_framework',

    # apps
    'app',
    'SiteServe',
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

ROOT_URLCONF = 'dj.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'dj.wsgi.application'


# Database
DATABASES = {
    # TODO - add postgresql
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    # { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    # { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    # { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
if IS_LOCAL := os.getenv('IS_LOCAL', False) == 'True':
    STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]  # in settings.py
else:
    STATIC_ROOT = os.path.join(BASE_DIR, "static/")

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Rest Framework
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        # TODO change to IsAuthenticatedSallaUser
        # because it can be another type of user
        'rest_framework.permissions.IsAuthenticated'
    ],

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'app.authentication.TokenAuthSupportCookie',
    ],

    'EXCEPTION_HANDLER': 'app.views.exception_handler',
}

# Log Setup
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'main_formatter': {
            'format': '{asctime} - {levelname} - {module} - {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'main_formatter',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/info.log'),
            'formatter': 'main_formatter',
        }
    },

    'loggers': {
        'main': {
            'handlers': ['file', 'console'] if DEBUG else ['file'],
            'propagate': True,
            'level': 'INFO'
        }
    }
}


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')



# Celery configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'  # Replace with your Redis server address if needed
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'  # Replace with your Redis server address if needed
CELERY_TIMEZONE = 'UTC'  # Use your preferred timezone

