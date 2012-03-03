import os.path

from django.conf import settings

__all__ = ['COUNTRY_SOURCES', 'CITY_SOURCES', 'ENABLE_CITY', 'SOURCES', 'DATA_DIR']

COUNTRY_SOURCES = getattr(settings, 'CITIES_LIGHT_COUNTRY_SOURCES',
    ['http://download.geonames.org/export/dump/countryInfo.txt'])
CITY_SOURCES = getattr(settings, 'CITIES_LIGHT_CITY_SOURCES', 
    ['http://download.geonames.org/export/dump/cities15000.zip'])

ENABLE_CITY = getattr(settings, 'CITIES_LIGHT_ENABLE_CITY', True)

SOURCES = list(COUNTRY_SOURCES) + list(CITY_SOURCES)

DATA_DIR = getattr(settings, 'CITIES_LIGHT_DATA_DIR',
    os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')))

if hasattr(settings, 'AJAX_LOOKUP_CHANNELS'):
    settings.AJAX_LOOKUP_CHANNELS['cities_light_country'] = (
        'cities_light.lookups', 'CountryLookup')
    if ENABLE_CITY:
        settings.AJAX_LOOKUP_CHANNELS['cities_light_city'] = (
            'cities_light.lookups', 'CityLookup')
