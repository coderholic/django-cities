"""
Django settings for test_project project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '&bloxby)1edwp08=5pwdd9(s1b)y^nwma6f*c&48w99-(z!7&='

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'cities',
    'model_utils',
    'test_app',
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

ROOT_URLCONF = 'test_app.urls'

WSGI_APPLICATION = 'test_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'django_cities',
        'USER': os.environ.get('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', ''),
        'HOST': '127.0.0.1',
        'PORT': 5432,
    }
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


# Logging:

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'ERROR',
        'handlers': ['console'],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'tests': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'cities': {
            'level': os.environ.get('TRAVIS_LOG_LEVEL', 'INFO'),
            'handlers': ['console'],
            'propagate': False,
        },
    },
}
# Cities config:
travis_commit = os.environ.get('TRAVIS_COMMIT')
travis_repo_slug = os.environ.get('TRAVIS_REPO_SLUG', 'coderholic/django-cities')
travis_repo_branch = os.environ.get('TRAVIS_PULL_REQUEST_BRANCH', '')
if travis_repo_branch == '':
    travis_repo_branch = os.environ.get('TRAVIS_BRANCH', os.environ.get('TRAVIS_REPO_BRANCH', 'master'))
if os.environ.get('CITIES_DATA_URL_BASE', False):
    url_base = os.environ.get('CITIES_DATA_URL_BASE')
elif travis_commit and travis_repo_slug:
    url_base = 'https://raw.githubusercontent.com/{repo_slug}/{commit_id}/test_project/data/'.format(
        repo_slug=travis_repo_slug, commit_id=travis_commit)
else:
    url_base = "https://raw.githubusercontent.com/{repo_slug}/{branch_name}/test_project/data/".format(
        repo_slug=travis_repo_slug,
        branch_name=travis_repo_branch)

CITIES_FILES = {
    'country': {
        'filename': 'countryInfo.txt',
        'urls': [url_base + '{filename}', ],
    },
    'region': {
        'filename': 'admin1CodesASCII.txt',
        'urls': [url_base + '{filename}', ],
    },
    'subregion': {
        'filename': 'admin2Codes.txt',
        'urls': [url_base + '{filename}', ],
    },
    'city': {
        'filename': 'cities1000.txt',
        'urls': [url_base + '{filename}', ],
    },
    'hierarchy': {
        'filename': 'hierarchy.txt',
        'urls': [url_base + '{filename}', ],
    },
    'alt_name': {
        'filename': 'alternateNames.txt',
        'urls': [url_base + '{filename}', ],
    },
    'postal_code': {
        'filename': 'allCountries.txt',
        'urls': [url_base + '{filename}', ],
    }
}

CITIES_LOCALES = ['en', 'und', 'link']
