import os.path

from django.conf import settings

"""
This settings file requires one setting: CITIES_LIGHT_CITY_SOURCES
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

class MissingSetting(Exception):
    def __init__(self, setting):
        message = 'Required setting %s is undefined.' % setting
        message += ' Refer to the documentation for help setting it.'
        super(MissingSetting, self).__init__(message)

try:
    # should be an iterable of stuff like http://download.geonames.org/export/zip/DE.zip
    CITY_SOURCES = settings.CITIES_LIGHT_CITY_SOURCES
except AttributeError:
    raise MissingSetting('CITIES_LIGHT_CITY_SOURCES')

COUNTRY_SOURCES = getattr(settings, 'CITIES_LIGHT_COUNTRY_SOURCES',
    ['http://download.geonames.org/export/dump/countryInfo.txt'])

SKIP_POSTAL_CODE = getattr(settings, 'CITIES_LIGHT_SKIP_POSTAL_CODES', False)

SOURCES = list(COUNTRY_SOURCES) + list(CITY_SOURCES)

WORK_DIR = getattr(settings, 'CITIES_LIGHT_WORK_DIR',
    os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'var')))
