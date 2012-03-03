import os.path

from django.conf import settings

"""
To populate cities, you should use: CITIES_LIGHT_CITY_SOURCES.
You can set it as such::

    CITIES_LIGHT_CITY_SOURCES = (
        'http://download.geonames.org/export/zip/VI.zip',
        'http://download.geonames.org/export/zip/RU.zip',
        'http://download.geonames.org/export/zip/DE.zip',
        # and so on
    )

If you want them all::

    CITIES_LIGHT_CITY_SOURCES = (
        'http://download.geonames.org/export/zip/allCountries.zip',
    )
"""

CITY_SOURCES = getattr(settings, 'CITIES_LIGHT_CITY_SOURCES', [])
COUNTRY_SOURCES = getattr(settings, 'CITIES_LIGHT_COUNTRY_SOURCES',
    ['http://download.geonames.org/export/dump/countryInfo.txt'])

ENABLE_ZIP = getattr(settings, 'CITIES_LIGHT_ENABLE_ZIP', False)
ENABLE_CITY = ENABLE_ZIP or getattr(settings, 'CITIES_LIGHT_ENABLE_CITY', True)

SOURCES = list(COUNTRY_SOURCES) + list(CITY_SOURCES)

DATA_DIR = getattr(settings, 'CITIES_LIGHT_DATA_DIR',
    os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'var')))

if hasattr(settings, 'AJAX_LOOKUP_CHANNELS'):
    settings.AJAX_LOOKUP_CHANNELS['cities_light.Country'] = (
        'cities_light.lookups', 'CountryLookup'),
    if ENABLE_CITY:
        settings.AJAX_LOOKUP_CHANNELS['cities_light.City'] = (
            'cities_light.lookups', 'CityLookup'),
    if ENABLE_ZIP:
        settings.AJAX_LOOKUP_CHANNELS['cities_light.Zip'] = (
            'cities_light.lookups', 'ZipLookup'),
