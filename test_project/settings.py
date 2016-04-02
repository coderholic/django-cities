# Django settings for test_project project.

import os
import sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'mzdvd*#0=$g(-!v_vj_7^(=zrh3klia(u&amp;cqd3nr7p^khh^ui#'

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cities_light',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'urls'

WSGI_APPLICATION = 'wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.' + os.environ.get('DB_ENGINE', 'sqlite3'),
        'NAME': os.environ.get('DB_NAME', 'db.sqlite'),
        'USER': os.environ.get('DB_USER', ''),
    }
}

if sys.version_info[0] < 3 and 'mysql' in DATABASES['default']['ENGINE']:
    DATABASES['default']['OPTIONS'] = {
        'autocommit': True,
    }


# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.request': {
            'handlers':['console'],
            'propagate': True,
            'level':'DEBUG',
        },
        'cities_light': {
            'handlers':['console'],
            'propagate': True,
            'level':'WARNING',
        },
    }
}

if os.environ.get('CI', False):
    CITIES_LIGHT_TRANSLATION_LANGUAGES=['fr', 'ru']

    FIXTURE_DIR = os.path.abspath(
        os.path.join(BASE_DIR, 'cities_light', 'tests', 'fixtures')
    )

    FIXTURE_DIRS = [FIXTURE_DIR]

    CITIES_LIGHT_CITY_SOURCES = ['file://%s/angouleme_city.txt' % FIXTURE_DIR]
    CITIES_LIGHT_REGION_SOURCES = ['file://%s/angouleme_region.txt' % FIXTURE_DIR]
    CITIES_LIGHT_COUNTRY_SOURCES = ['file://%s/angouleme_country.txt' % FIXTURE_DIR]
    CITIES_LIGHT_TRANSLATION_SOURCES = ['file://%s/angouleme_translations.txt' % FIXTURE_DIR]

    LOGGING['loggers']['cities_light']['level'] = 'DEBUG'

    INSTALLED_APPS += ('dbdiff',)
