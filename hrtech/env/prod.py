from hrtech import base as base_settings

BASE_DIR = base_settings.BASE_DIR
SECRET_KEY = base_settings.SECRET_KEY
INSTALLED_APPS = base_settings.INSTALLED_APPS
AUTH_USER_MODEL = base_settings.AUTH_USER_MODEL
MIDDLEWARE = base_settings.MIDDLEWARE
ROOT_URLCONF = base_settings.ROOT_URLCONF
TEMPLATES = base_settings.TEMPLATES
WSGI_APPLICATION = base_settings.WSGI_APPLICATION
AUTH_PASSWORD_VALIDATORS = base_settings.AUTH_PASSWORD_VALIDATORS
UNFOLD = base_settings.UNFOLD
LANGUAGE_CODE = base_settings.LANGUAGE_CODE
TIME_ZONE = base_settings.TIME_ZONE
USE_I18N = base_settings.USE_I18N
USE_TZ = base_settings.USE_TZ
STATIC_URL = base_settings.STATIC_URL
STATIC_ROOT = base_settings.STATIC_ROOT
MEDIA_URL = base_settings.MEDIA_URL
MEDIA_ROOT = base_settings.MEDIA_ROOT
DEFAULT_AUTO_FIELD = base_settings.DEFAULT_AUTO_FIELD
APPEND_SLASH = base_settings.APPEND_SLASH
CORS_ALLOWED_ORIGINS = base_settings.CORS_ALLOWED_ORIGINS
CORS_ALLOW_CREDENTIALS = base_settings.CORS_ALLOW_CREDENTIALS
CORS_ALLOW_METHODS = base_settings.CORS_ALLOW_METHODS
CORS_ALLOW_HEADERS = base_settings.CORS_ALLOW_HEADERS
REST_FRAMEWORK = getattr(base_settings, "REST_FRAMEWORK", {})

DEBUG = False
ALLOWED_HOSTS = ["*"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    },
}