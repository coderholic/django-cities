import urllib
import time
import os
import os.path
import logging
import zipfile
import optparse

from django.db import models
from django.core.management.base import BaseCommand
from django.utils.encoding import force_unicode

from ...models import *
from ...settings import *

class Command(BaseCommand):
    args = '''
[--force-all] [--force-import-all \\]
                              [--force-import allCountries.txt FR.zip ...] \\
                              [--force allCountries.txt FR.zip ...]
    '''.strip()
    help = '''
Download all files in CITIES_LIGHT_COUNTRY_SOURCES if they were updated or if 
--force-all option was used.
Import country data if they were downloaded or if --force-import-all was used.

Same goes for CITIES_LIGHT_CITY_SOURCES.

It is possible to force the download of some files which have not been updated
on the server:

    manage.py --force FR.zip countryInfo.txt

It is possible to force the import of files which weren't downloaded using the 
--force-import option:

    manage.py --force-import FR.zip countryInfo.txt
    '''.strip()

    logger = logging.getLogger('cities_light')

    option_list = BaseCommand.option_list + (
        optparse.make_option('--force-import-all', action='store_true', default=False,
            help='Import even if files are up-to-date.'
        ),
        optparse.make_option('--force-all', action='store_true', default=False,
            help='Download and import if files are up-to-date.'
        ),
        optparse.make_option('--force-import', action='append', default=[],
            help='Import even if filenames matching FORCE_IMPORT are up-to-date.'
        ),
        optparse.make_option('--force', action='append', default=[],
            help='Download and import if filenames matching FORCE are up-to-date.'
        ),
    )

    def handle(self, *args, **options):
        if not os.path.exists(DATA_DIR):
            self.logger.info('Creating %s' % DATA_DIR)
            os.mkdir(DATA_DIR)

        for url in SOURCES:
            destination_file_name = url.split('/')[-1]
            destination_file_path = os.path.join(DATA_DIR, destination_file_name)
            
            force = options['force_all'] or destination_file_name in options['force']
            downloaded = self.download(url, destination_file_path, force)
            
            if destination_file_name.split('.')[-1] == 'zip':
                destination_file_name = destination_file_name.replace('zip', 'txt')
                self.extract(destination_file_path, destination_file_name)
                destination_file_path = os.path.join(DATA_DIR, destination_file_name)

            force_import = options['force_import_all'] or \
                destination_file_name in options['force_import']
            if downloaded or force_import:
                self.logger.info('Importing %s' % destination_file_name)

                if url in CITY_SOURCES:
                    self.city_import(destination_file_path)
                elif url in COUNTRY_SOURCES:
                    self.country_import(destination_file_path)
  
    def download(self, url, path, force=False):
        remote_file = urllib.urlopen(url)
        remote_time = time.strptime(remote_file.headers['last-modified'], 
            '%a, %d %b %Y %H:%M:%S %Z')
        remote_size = int(remote_file.headers['content-length'])

        if os.path.exists(path) and not force:
            local_time = time.gmtime(os.path.getmtime(path))
            local_size = os.path.getsize(path)

            if local_time >= remote_time and local_size == remote_size:
                self.logger.warning('Assuming local download is up to date for %s' % url)
                return False

        self.logger.info('Downloading %s into %s' % (url, path))
        with open(path, 'wb') as local_file:
            chunk = remote_file.read()
            while chunk:
                local_file.write(chunk)
                chunk = remote_file.read()
        
        return True

    def extract(self, zip_path, file_name):
        destination = os.path.join(DATA_DIR, file_name)
        
        self.logger.info('Extracting %s from %s into %s' % (file_name, zip_path, destination))

        with zipfile.ZipFile(zip_path) as zip_file:
            with open(destination, 'wb') as destination_file:
                destination_file.write(zip_file.read(file_name))
    
    def country_import(self, file_path):
        for items in self.parse(file_path):
            try:
                country = Country.objects.get(code2=items[0])
            except Country.DoesNotExist:
                country = Country(code2=items[0])

            country.name = items[4]
            country.code3 = items[1]
            country.continent = items[8]
            country.tld = items[9][1:] # strip the leading
            country.save()

    def city_import(self, file_path):
        country = previous_city = previous_zip = False

        for items in self.parse(file_path):
            if not country or country.code2 != items[0]:
                country = Country.objects.get(code2=items[0])

            if not previous_city or force_unicode(items[2]) != previous_city.name:
                city, created = City.objects.get_or_create(name=items[2], 
                    country=country)
            else:
                city = previous_city

            if ENABLE_POSTAL_CODE:
                if not previous_zip or items[1] != previous_zip:
                    zip, created = Zip.objects.get_or_create(
                        code=items[1], city=city)

                    if created or zip.name != force_unicode(items[2]):
                        zip.name = items[2]
                        zip.save()
                    
                    previous_zip = zip.code

            previous_city = city

    def parse(self, file_path):
        file = open(file_path, 'r')
        line = True

        while line:
            line = file.readline().strip()
            
            if len(line) < 1 or line[0] == '#':
                continue

            yield [e.strip() for e in line.split('\t')]
