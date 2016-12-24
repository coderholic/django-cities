import os
import django


def rel(path):
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), path)


DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'HOST': 'localhost',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'OPTIONS': {
            'autocommit': True,
        }
    }
}

TEMPLATE_DIRS = (rel("templates"),)
TIME_ZONE = 'UTC'
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

SECRET_KEY = 'YOUR_SECRET_KEY'

ROOT_URLCONF = 'urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.gis',
    'cities',
)

if django.VERSION < (1, 7):
    INSTALLED_APPS += (
        'south',
    )

CITIES_POSTAL_CODES = ['ALL']
CITIES_LOCALES = ['ALL']

CITIES_PLUGINS = [
    'cities.plugin.postal_code_ca.Plugin',  # Canada postal codes need region codes remapped to match geonames
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'log_to_stdout': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'cities': {
            'handlers': ['log_to_stdout'],
            'level': 'INFO',
            'propagate': True,
        }
    }
}
