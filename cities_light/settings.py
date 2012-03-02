import os.path

from django.conf import settings

COUNTRY_SOURCES = getattr(settings, 'CITIES_LIGHT_COUNTRY_INFO_SOURCES',
    ['http://download.geonames.org/export/dump/countryInfo.txt'])

CITY_SOURCES = getattr(settings, 'CITIES_LIGHT_CITY_SOURCES',
    ['http://download.geonames.org/export/zip/FR.zip'])

SKIP_POSTAL_CODE = getattr(settings, 'CITIES_LIGHT_SKIP_POSTAL_CODES', False)

SOURCES = list(COUNTRY_SOURCES) + list(CITY_SOURCES)

WORK_DIR = getattr(settings, 'CITIES_LIGHT_WORK_DIR',
    os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'var')))
