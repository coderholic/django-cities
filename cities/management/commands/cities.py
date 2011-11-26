"""
GeoNames city data import script.
Requires the following files:

http://download.geonames.org/export/dump/
- Countries:            countryInfo.txt
- Regions:              admin1CodesASCII.txt
- Cities / Districts:   cities5000.zip
- Localization:         alternateNames.zip
"""

import os
import sys
import urllib
import logging
import zipfile
import time
from optparse import make_option
from django.core.management.base import BaseCommand
from django.template.defaultfilters import slugify
from ...models import *

class Command(BaseCommand):
    app_dir = os.path.normpath(os.path.dirname(os.path.realpath(__file__)) + '/../..')
    data_dir = os.path.join(app_dir, 'data')
    logger = logging.getLogger("cities")
    url_base = 'http://download.geonames.org/export/dump/'
    
    option_list = BaseCommand.option_list + (
        make_option('--force', action='store_true', default=False,
            help='Import even if files are up-to-date.'),
    )
    
    def handle(self, *args, **options):
        self.options = options
        self.import_countries()
        self.import_regions()
        self.import_cities()
        self.import_geo_alt_name()
        
    def download(self, filename):
        web_file = urllib.urlopen(self.url_base + filename)
        web_file_time = time.strptime(web_file.headers['last-modified'], '%a, %d %b %Y %H:%M:%S %Z')
        web_file_size = int(web_file.headers['content-length'])

        file_exists = False
        try:
            file_time = time.gmtime(os.path.getmtime(os.path.join(self.data_dir, filename)))
            file_size = os.path.getsize(os.path.join(self.data_dir, filename))
            if file_time >= web_file_time and file_size == web_file_size:
                self.logger.info("File up-to-date: " + filename)
                file_exists = True
                if not self.options['force']: return None
        except: pass

        if not file_exists:
            self.logger.info("Downloading: " + filename)
            if not os.path.exists(self.data_dir):
                os.makedirs(self.data_dir)
            file = open(os.path.join(self.data_dir, filename), 'w+b')
            file.write(web_file.read())
            file.seek(0)
        else:
            file = open(os.path.join(self.data_dir, filename), 'rb')

        return file
        
    def import_countries(self):
        file = self.download('countryInfo.txt')
        if not file: return
        
        self.logger.info("Importing country data")
        for line in file:
            if len(line) < 1 or line[0] == '#': continue
            items = [e.strip() for e in line.decode("utf-8").split('\t')]
            
            country = Country()
            try: country.id = int(items[16])
            except: continue
            country.name = items[4]
            country.slug = slugify(country.name)
            country.code = items[0]
            country.population = items[7]
            country.continent = items[8]
            country.tld = items[9][1:] # strip the leading .
            
            country.save()
            self.logger.debug(u"Added country: {}, {}".format(country.code, country))

        file.close()

    def import_regions(self):
        file = self.download('admin1CodesASCII.txt')
        if not file: return
        
        self.logger.info("Building country index")
        country_objects = {}
        for obj in Country.objects.all():
            country_objects[obj.code] = obj
                
        self.logger.info("Importing region data")
        for line in file:
            if len(line) < 1 or line[0] == '#': continue
            items = [e.strip() for e in line.split('\t')]
            
            region = Region()
            region.id = items[3]
            region.name = items[2]
            region.name_std = items[1]
            region.slug = slugify(region.name)
            region.code = items[0]
            try: region.country = country_objects[region.code[:2]]
            except:
                self.logger.warning(u"Region: {}: Cannot find country: {} -- skipping".format(region.name, region.code[:2]))
                continue

            region.save()
            self.logger.debug(u"Added region: {}, {}".format(region.code, region))
        
        file.close()
        
    def import_cities(self):
        file = self.download('cities5000.zip')
        if not file: return
        
        zip = zipfile.ZipFile(file)
        data = zip.read('cities5000.txt').split('\n')
        zip.close()
        file.close()
        
        self.logger.info("Building region index")
        region_objects = {}
        for obj in Region.objects.all():
            region_objects[obj.code] = obj
            
        self.logger.info("Importing city data")
        for line in data:
            if len(line) < 1 or line[0] == '#': continue
            items = [e.strip() for e in line.split('\t')]
            
            admin_type = items[11]
            type = items[7]

            # See http://www.geonames.org/export/codes.html
            if type not in ['PPL', 'PPLA', 'PPLC', 'PPLA2', 'PPLA3', 'PPLA4']: continue
                
            city = City()
            city.id = items[0]
            city.name = items[2]
            city.name_std = items[1]
            city.slug = slugify(city.name)
            city.location = Point(float(items[5]), float(items[4]))
            city.population = items[14]

            # Try more specific region first
            region = None
            if items[11]:
                try:
                    code = "{}.{}".format(items[8], items[11])
                    region = region_objects[code]
                except: pass
            if not region:
                try:
                    code = "{}.{}".format(items[8], items[10])
                    region = region_objects[code]
                except:
                    self.logger.warning(u"City: {}: Cannot find region: {} -- skipping".format(city.name, code))
                    continue
                    
            city.region = region
            city.save()
            self.logger.debug(u"Added city: {}".format(city))
                
        self.import_districts(data, region_objects)
    
    def import_districts(self, data, region_objects):

        self.logger.info("Importing district data")
        for line in data:
            if len(line) < 1 or line[0] == '#': continue
            items = [e.strip() for e in line.split('\t')]

            admin_type = items[11]
            type = items[7]

            # See http://www.geonames.org/export/codes.html
            if type not in ['PPLX']: continue
                
            district = District()
            district.id = items[0]
            district.name = items[2]
            district.name_std = items[1]
            district.slug = slugify(district.name)
            district.location = Point(float(items[5]), float(items[4]))
            district.population = items[14]
            
            # Try more specific region first
            region = None
            if items[11]:
                try:
                    code = "{}.{}".format(items[8], items[11])
                    region = region_objects[code]
                except: pass
            if not region:
                try:
                    code = "{}.{}".format(items[8], items[10])
                    region = region_objects[code]
                except:
                    self.logger.warning(u"District: {}: Cannot find region: {} -- skipping".format(district.name, code))
                    continue

            # Set the nearest city
            district.city = City.objects.filter(population__gt=125000).distance(district.location).order_by('distance')[0] 
            district.save()
            self.logger.debug(u"Added district: {}".format(district))
            
    def import_geo_alt_name(self):
        file = self.download('alternateNames.zip')
        if not file: return
        
        zip = zipfile.ZipFile(file)
        data = zip.read('alternateNames.txt').split('\n')
        zip.close()
        file.close()
        
        self.logger.info("Building geo index")
        geo_id_info = {}
        for type_ in geo_alt_names:
            for obj in type_.objects.all():
                geo_id_info[obj.id] = {
                    'type': type_,
                    'object': obj,
                }
        
        self.logger.info("Importing alternate name data")
        for line in data:
            if len(line) < 1 or line[0] == '#': continue
            items = [e.strip() for e in line.split('\t')]
                
            # Only get names for languages in use
            locale = items[2]
            if not locale: locale = 'und'
            if not locale in settings.CITIES_LOCALES: continue
            
            # Check if known geo id
            geo_id = int(items[1])
            try: geo_info = geo_id_info[geo_id]
            except: continue
            
            alt_type = geo_alt_names[geo_info['type']][locale]
            alt = alt_type()
            alt.id = items[0]
            alt.geo = geo_info['object']
            alt.name = items[3]
            alt.is_preferred = items[4]
            alt.is_short = items[5]
            alt.save()
            self.logger.debug(u"Added alt name: {}, {} ({})".format(locale, alt, alt.geo.name))
            
