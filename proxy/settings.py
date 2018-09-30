import os
from datetime import timedelta
from decouple import config, Csv

# Django settings for proxy project.

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEBUG = config('DEBUG', default=False, cast=bool)

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': config('DB_NAME'),                  # Or path to database file if using sqlite3.
        'USER': config('DB_USER'),                  # Not used with sqlite3.
        'PASSWORD': config('DB_PASSWORD'),          # Not used with sqlite3.
        'HOST': config('DB_HOST'),                  # Set to empty string for localhost. Not used with sqlite3.
        'PORT': config('DB_PORT', default=''),      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Paris'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(BASE_DIR, '../static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = config('SECRET_KEY')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, '../templates/'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
            'debug': DEBUG,
        },
    },
]

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'proxy.urls'

# Python dotted path to the WSGI application used by Django's runserver.
#WSGI_APPLICATION = 'proxy.wsgi.application'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    # 'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'django.contrib.gis',
    'pmessages',
    'django.contrib.humanize',
    'storages',
    'rest_framework',
    'sslserver',
    'django_generate_secret_key',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LEVEL = 'DEBUG' if DEBUG else 'ERROR'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': LEVEL,
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            },
        'django.server': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': True,
        },
        'pmessages': {
            'handlers': ['console'],
            'level': LEVEL,
        }
    }
}

# Required to be able to serialize the session using the DB backend.
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

# Mininum message display radius (meters)
PROXY_RADIUS_MIN = config('PROXY_RADIUS_MIN', default=64, cast=int)
# Maximum message display radius (meters)
PROXY_RADIUS_MAX = config('PROXY_RADIUS_MAX', default=524288, cast=int)
# Thresholds dictionnary, composed as timedelta object as key
# and message count as value.
PROXY_THRESHOLDS = {
        timedelta(hours=1): 3,
        timedelta(hours=4): 5,
        timedelta(days=1):  7
        }
# Proxy user expiration time, in minutes.
PROXY_USER_EXPIRATION = config('PROXY_USER_EXPIRATION', default=300, cast=int)
# Proxy user expiration refresh, in minutes
PROXY_USER_REFRESH = config('PROXY_USER_REFRESH', default=5, cast=int)
# Proxy index update expiration in minutes.
PROXY_INDEX_EXPIRATION = config('PROXY_INDEX_EXPIRATION', default=5, cast=int)
# GeoIP
GEOIP_PATH = os.path.join(BASE_DIR, 'data/geoip')
# Static files to S3
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
AWS_S3_REGION_NAME = 'eu-west-1'
AWS_S3_HOST = 's3-eu-west-1.amazonaws.com'
STATIC_URL = '/static/'
import boto.s3.connection
AWS_S3_CALLING_FORMAT = boto.s3.connection.OrdinaryCallingFormat()
# Allowed hosts for POST Protection
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())
# CSRF
CSRF_TRUSTED_ORIGINS = ['localhost:3000', 'prxi.net']
