"""
GeoNames city data import script.
Requires the following files:

http://download.geonames.org/export/dump/
- Countries:            countryInfo.txt
- Regions:              admin1CodesASCII.txt, admin2Codes.txt
- Cities:               cities5000.zip
- Districts:            hierarchy.zip
- Localization:         alternateNames.zip

http://download.geonames.org/export/zip/
- Postal Codes:         allCountries.zip
"""

import os
import sys
import urllib
import logging
import zipfile
import time
from collections import namedtuple, defaultdict
from optparse import make_option
from django.core.management.base import BaseCommand
from django.utils.encoding import force_unicode
from django.template.defaultfilters import slugify
from django.db import connection
from django.contrib.gis.gdal.envelope import Envelope
from ...conf import *
from ...models import *
from ...util import geo_distance

class Command(BaseCommand):
    app_dir = os.path.normpath(os.path.dirname(os.path.realpath(__file__)) + '/../..')
    data_dir = os.path.join(app_dir, 'data')
    logger = logging.getLogger("cities")
    
    option_list = BaseCommand.option_list + (
        make_option('--force', action='store_true', default=False,
            help='Import even if files are up-to-date.'
        ),
        make_option('--import', metavar="DATA_TYPES", default='all',
            help =  'Selectively import data. Comma separated list of data types: '
                    + str(import_opts).replace("'",'')
        ),
        make_option('--flush', metavar="DATA_TYPES", default='',
            help =  "Selectively flush data. Comma separated list of data types."
        ),
    )
    
    def handle(self, *args, **options):
        import ipdb; ipdb.set_trace()
        self.download_cache = {}
        self.options = options
        
        self.force = self.options['force']
        
        self.flushes = [e for e in self.options['flush'].split(',') if e]
        if 'all' in self.flushes: self.flushes = import_opts_all
        for flush in self.flushes:
            func = getattr(self, "flush_" + flush)
            func()
            
        self.imports = [e for e in self.options['import'].split(',') if e]
        if 'all' in self.imports: self.imports = import_opts_all
        if self.flushes: self.imports = []
        for import_ in self.imports:
            func = getattr(self, "import_" + import_)
            func()
        
    def call_hook(self, hook, *args, **kwargs):
        for plugin in settings.plugins[hook]:
            try:
                func = getattr(plugin,hook)
                func(self, *args, **kwargs)
            except HookException as e:
                error = str(e)
                if error: self.logger.error(error)
                return False
        return True
        
    def download(self, filekey):
        filename = settings.files[filekey]['filename']
        web_file = None
        urls = [e.format(filename=filename) for e in settings.files[filekey]['urls']]
        for url in urls:
            try:
                web_file = urllib.urlopen(url)
                if 'html' in web_file.headers['content-type']: raise Exception()
                break
            except:
                web_file = None
                continue
        else:
            self.logger.error("Web file not found: {}. Tried URLs:\n{}".format(filename, '\n'.join(urls)))
            
        uptodate = False
        filepath = os.path.join(self.data_dir, filename)
        if web_file is not None:
            web_file_time = time.strptime(web_file.headers['last-modified'], '%a, %d %b %Y %H:%M:%S %Z')
            web_file_size = int(web_file.headers['content-length'])
            if os.path.exists(filepath):
                file_time = time.gmtime(os.path.getmtime(filepath))
                file_size = os.path.getsize(filepath)
                if file_time >= web_file_time and file_size == web_file_size:
                    self.logger.info("File up-to-date: " + filename)
                    uptodate = True
        else:
            self.logger.warning("Assuming file is up-to-date")
            uptodate = True
            
        if not uptodate and web_file is not None:
            self.logger.info("Downloading: " + filename)
            if not os.path.exists(self.data_dir):
                os.makedirs(self.data_dir)
            file = open(os.path.join(self.data_dir, filename), 'wb')
            file.write(web_file.read())
            file.close()
        elif not os.path.exists(filepath):
            raise Exception("File not found and download failed: " + filename)
            
        return uptodate
    
    def download_once(self, filekey):
        if filekey in self.download_cache: return self.download_cache[filekey]
        uptodate = self.download_cache[filekey] = self.download(filekey)
        return uptodate
            
    def get_data(self, filekey):
        filename = settings.files[filekey]['filename']
        file = open(os.path.join(self.data_dir, filename), 'rb')
        name, ext = filename.rsplit('.',1)
        if (ext == 'zip'):
            zip = zipfile.ZipFile(file)
            data = zip.read(name + '.txt').split('\n')
            zip.close()
        else:
            data = file.read().split('\n')
        file.close()
        return data
        
    def import_country(self):
        uptodate = self.download('country')
        if uptodate and not self.force: return
        data = self.get_data('country')
        
        self.logger.info("Importing country data")
        for line in data:
            if len(line) < 1 or line[0] == '#': continue
            items = [e.strip() for e in line.split('\t')]
            if not self.call_hook('country_pre', items): continue
            
            country = Country()
            try: country.id = int(items[16])
            except: continue
            country.name = items[4]
            country.slug = slugify(country.name)
            country.code = items[0]
            country.population = items[7]
            country.continent = items[8]
            country.tld = items[9][1:] # strip the leading .
            
            if not self.call_hook('country_post', country, items): continue 
            country.save()
            self.logger.debug("Added country: {}, {}".format(country.code, country))

    def build_country_index(self):
        if hasattr(self, 'country_index'): return
        
        self.logger.info("Building country index")
        self.country_index = {}
        for obj in Country.objects.all():
            self.country_index[obj.code] = obj
            
    def import_city_common(self, city, items):
        class_ = city.__class__
        city.id = int(items[0])
        city.name = items[2]
        city.name_std = items[1]
        city.slug = slugify(city.name)
        city.location = Point(float(items[5]), float(items[4]))
        city.population = items[14]

        # Find country
        country = None
        country_code = items[8]
        try: country = self.country_index[country_code]
        except:
            self.logger.warning("{}: {}: Cannot find country: {} -- skipping".format(class_.__name__, city.name, country_code))
            return None
        if class_ is City: city.country = country
        
        return city
            
    def import_city(self):            
        uptodate = self.download_once('city')
        if uptodate and not self.force: return
        data = self.get_data('city')
        
        self.build_country_index()

        self.logger.info("Importing city data")
        for line in data:
            if len(line) < 1 or line[0] == '#': continue
            items = [e.strip() for e in line.split('\t')]
            if not self.call_hook('city_pre', items): continue
            
            type = items[7]
            if type not in city_types: continue
            
            city = self.import_city_common(City(), items)
            if not city: continue
            
            if not self.call_hook('city_post', city, items): continue
            city.save()
            self.logger.debug("Added city: {}".format(city))
           
    def import_postal_code(self):
        uptodate = self.download('postal_code')
        if uptodate and not self.force: return
        data = self.get_data('postal_code')
        
        self.build_country_index()
        self.build_region_index()
                
        self.logger.info("Importing postal codes")
        for line in data:
            if len(line) < 1 or line[0] == '#': continue
            items = [e.strip() for e in line.split('\t')]
            if not self.call_hook('postal_code_pre', items): continue
            
            country_code = items[0]
            if country_code not in settings.postal_codes: continue
            
            # Find country
            code = items[1]
            country = None
            try: country = self.country_index[country_code]
            except:
                self.logger.warning("Postal code: {}: Cannot find country: {} -- skipping".format(code, country_code))
                continue
            
            pc_type = postal_codes[country_code]
            pc = pc_type()
            pc.country = country
            pc.code = code
            pc.name = items[2]
            pc.region_0_name = items[3]
            pc.region_1_name = items[5]
            pc.region_2_name = items[7]
            
            try: pc.location = Point(float(items[10]), float(items[9]))
            except:
                self.logger.warning("Postal code: {}, {}: Invalid location ({}, {})".format(pc.country, pc.code, items[10], items[9]))
                pc.location = Point(0,0)
                
            # Find region, search highest level first
            region = None
            item_offset = 4
            for level in reversed(range(2)):
                if not items[item_offset+level*2]: continue
                try:
                    code = '.'.join([country_code] + [items[item_offset+i*2] for i in range(level+1)])
                    region = self.region_index[code]
                    break
                except:
                    self.logger.log(logging.DEBUG if level else logging.WARNING, # Escalate if all levels failed
                                    "Postal code: {}, {}: Cannot find region {}: {}".format(pc.country, pc.code, level, code))
            pc.region = region
        
            if not self.call_hook('postal_code_post', pc, items): continue
            pc.save()
            self.logger.debug("Added postal code: {}, {}".format(pc.country, pc))
            
    def flush_country(self):
        self.logger.info("Flushing country data")
        Country.objects.all().delete()
        
    def flush_city(self):
        self.logger.info("Flushing city data")
        City.objects.all().delete()
    
    def flush_postal_code(self):
        self.logger.info("Flushing postal code data")
        [postal_code.objects.all().delete() for postal_code in postal_codes.values()]
    
