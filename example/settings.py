import os
def rel(path):
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), path)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'HOST': 'localhost',
        'NAME': 'geomium',
        'USER': 'geomium',
        'PASSWORD': 'ge0m1um',
        'OPTIONS': {
            'autocommit': True,
        }
    }
}

TEMPLATE_DIRS = (rel("templates"))
TIME_ZONE = 'UTC'
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

SECRET_KEY = 'YOUR_SECRET_KEY'
MIDDLEWARE_CLASSES = (
)

ROOT_URLCONF = 'examples.urls'

INSTALLED_APPS = (
    'cities',
)

CITIES_POSTAL_CODES = ['GB']
