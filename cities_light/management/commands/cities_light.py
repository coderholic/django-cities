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
    app_dir = os.path.normpath(os.path.dirname(os.path.realpath(__file__)) + '/../..')
    data_dir = os.path.join(app_dir, 'data')
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
        if not os.path.exists(WORK_DIR):
            self.logger.info('Creating %s' % WORK_DIR)
            os.mkdir(WORK_DIR)

        for url in SOURCES:
            destination_file_name = url.split('/')[-1]
            destination_file_path = os.path.join(WORK_DIR, destination_file_name)
            
            force = options['force_all'] or destination_file_name in options['force']
            downloaded = self.download(url, destination_file_path, force)
            
            if destination_file_name.split('.')[-1] == 'zip':
                destination_file_name = destination_file_name.replace('zip', 'txt')
                self.extract(destination_file_path, destination_file_name)
                destination_file_path = os.path.join(WORK_DIR, destination_file_name)

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
        destination = os.path.join(WORK_DIR, file_name)
        
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
        country = previous_city = previous_postal_code = False

        for items in self.parse(file_path):
            if not country or country.code2 != items[0]:
                country = Country.objects.get(code2=items[0])

            if not previous_city or force_unicode(items[3]) != previous_city.name:
                try:
                    city = City.objects.get(name=items[3], country=country)
                except City.DoesNotExist:
                    city = City(name=items[3], country=country)

                city.name = items[3]
                city.save()
            else:
                city = previous_city

            if not SKIP_POSTAL_CODE:
                if not previous_postal_code or items[1] != previous_postal_code:
                    postal_code, created = PostalCode.objects.get_or_create(code=items[1], 
                        city=city)
                    previous_postal_code = postal_code.code

            previous_city = city

    def parse(self, file_path):
        file = open(file_path, 'r')
        line = True

        while line:
            line = file.readline().strip()
            
            if len(line) < 1 or line[0] == '#':
                continue

            yield [e.strip() for e in line.split('\t')]
