import os.path

from django.conf import settings

SOURCE = getattr(settings, 'CITIES_LIGHT_SOURCE', 
    'http://download.geonames.org/export/zip/')
FILES = getattr(settings, 'CITIES_LIGHT_FILES', ['FR.zip'])
WORK_DIR = getattr(settings, 'CITIES_LIGHT_WORK_DIR',
    os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'var')))
