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
from ...conf import *
from ...models import *

class Command(BaseCommand):
    app_dir = os.path.normpath(os.path.dirname(os.path.realpath(__file__)) + '/../..')
    data_dir = os.path.join(app_dir, 'data')
    logger = logging.getLogger("cities")
    
    option_list = BaseCommand.option_list + (
        make_option('--force', action='store_true', default=False,
            help='Import even if files are up-to-date.'),
    )
    
    def handle(self, *args, **options):
        self.options = options
        self.import_countries()
        self.import_regions_0()
        self.import_regions_1()
        self.import_cities()
        self.import_geo_alt_name()
        self.import_postal_codes()
        
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
        
    def download(self, filename):
        web_file = None
        urls = [e.format(filename=filename) for e in globals()['urls'][filename]]
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
            self.logger.warning("Assuming file is up-to-date, use --force to import.")
            uptodate = True
            
        if not uptodate and web_file is not None:
            self.logger.info("Downloading: " + filename)
            if not os.path.exists(self.data_dir):
                os.makedirs(self.data_dir)
            file = open(os.path.join(self.data_dir, filename), 'w+b')
            file.write(web_file.read())
            file.seek(0)
        elif os.path.exists(filepath):
            file = open(os.path.join(self.data_dir, filename), 'rb')
        else:
            raise Exception("File not found and download failed: " + filename)
            
        return namedtuple('_', 'file, uptodate')(file, uptodate)
        
    def import_countries(self):
        file, uptodate = self.download('countryInfo.txt')[:2]
        if uptodate and not self.options['force']: return
        
        self.logger.info("Importing country data")
        for line in file:
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

        file.close()

    def import_region_common(self, region, level, items):
        region.id = int(items[3])
        region.name = items[2]
        region.name_std = items[1]
        region.slug = slugify(region.name)
        region.code = items[0]
        region.level = level
        
        # Find country
        country_code = region.code.split('.')[0]
        try: region.country = self.country_index[country_code]
        except:
            self.logger.warning("Region {}: {}: Cannot find country: {} -- skipping".format(level+1, region.name, country_code))
            return None
        
        # Find parent region, search highest level first
        for sublevel in reversed(range(level)):
            region_parent_code = '.'.join(region.code.split('.')[:sublevel+2])
            try:
                region.region_parent = self.region_index[region_parent_code]
                break
            except:
                self.logger.warning("Region {}: {}: Cannot find region {}: {}".format(sublevel+2, region.name, sublevel+1, region_parent_code))
            
        return region
    
    def build_country_index(self):
        if hasattr(self, 'country_index'): return
        
        self.logger.info("Building country index")
        self.country_index = {}
        for obj in Country.objects.all():
            self.country_index[obj.code] = obj
            
    def import_regions_0(self):
        file, uptodate = self.download('admin1CodesASCII.txt')[:2]
        if uptodate and not self.options['force']: return
                
        self.build_country_index()
                
        self.logger.info("Importing region 1 data")
        for line in file:
            if len(line) < 1 or line[0] == '#': continue
            items = [e.strip() for e in line.split('\t')]
            if not self.call_hook('region_pre', 0, items): continue
            
            region = self.import_region_common(Region(), 0, items)
            if not region: continue
            
            if not self.call_hook('region_post', 0, region, items): continue
            region.save()
            self.logger.debug("Added region 1: {}, {}".format(region.code, region))
        
        file.close()
        
    def build_region_index(self, level=None):
        if hasattr(self, 'region_index') and self.region_index_level == level: return
        
        if level is None:
            self.logger.info("Building region index")
            qset = Region.objects.all()
        else:
            self.logger.info("Building region {} index".format(level+1))
            qset = Region.objects.filter(level=level)
            
        self.region_index = {}
        for obj in qset:
            self.region_index[obj.code] = obj
        self.region_index_level = level
            
    def import_regions_1(self):
        file, uptodate = self.download('admin2Codes.txt')[:2]
        if uptodate and not self.options['force']: return
        
        self.build_country_index()
        self.build_region_index(0)
                
        self.logger.info("Importing region 2 data")
        for line in file:
            if len(line) < 1 or line[0] == '#': continue
            items = [e.strip() for e in line.split('\t')]
            if not self.call_hook('region_pre', 1, items): continue
            
            region = self.import_region_common(Region(), 1, items)
            if not region: continue  
            
            if not self.call_hook('region_post', 1, region, items): continue
            region.save()
            self.logger.debug("Added region 2: {}, {}".format(region.code, region))
        
        file.close()
        
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
        
        # Find region, search highest level first
        region = None
        item_offset = 10
        for level in reversed(range(2)):
            if not items[item_offset+level]: continue
            try:
                code = '.'.join([country_code] + [items[item_offset+i] for i in range(level+1)])
                region = self.region_index[code]
                break
            except:
                self.logger.warning("{}: {}: Cannot find region {}: {}".format(class_.__name__, city.name, level+1, code))
        if class_ is City: city.region = region
        
        return city
        
    def import_cities(self):
        file, uptodate = self.download('cities5000.zip')[:2]
        if uptodate and not self.options['force']: return
        
        zip = zipfile.ZipFile(file)
        data = zip.read('cities5000.txt').split('\n')
        zip.close()
        file.close()
        
        self.build_country_index()
        self.build_region_index()

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

        self.import_districts(data)
    
    def build_hierarchy(self):
        if hasattr(self, 'hierarchy'): return
        
        file = self.download('hierarchy.zip').file
        zip = zipfile.ZipFile(file)
        data = zip.read('hierarchy.txt').split('\n')
        zip.close()
        file.close()
        
        self.logger.info("Building hierarchy index")
        self.hierarchy = {}
        for line in data:
            if len(line) < 1 or line[0] == '#': continue
            items = [e.strip() for e in line.split('\t')]
            parent_id = int(items[0])
            child_id = int(items[1])
            self.hierarchy[child_id] = parent_id
            
    def import_districts(self, city_data):
        self.build_hierarchy()
            
        self.logger.info("Building city index")
        city_index = {}
        for obj in City.objects.all():
            city_index[obj.id] = obj
            
        self.logger.info("Importing district data")
        for line in city_data:
            if len(line) < 1 or line[0] == '#': continue
            items = [e.strip() for e in line.split('\t')]
            if not self.call_hook('district_pre', items): continue
            
            type = items[7]
            if type not in district_types: continue
            
            district = self.import_city_common(District(), items)
            if not district: continue
            
            # Find city
            try: district.city = city_index[self.hierarchy[district.id]]
            except:
                self.logger.warning("District: {}: Cannot find city in hierarchy, using nearest".format(district.name))
                district.city = City.objects.filter(population__gt=100000).distance(district.location).order_by('distance')[0]
            
            if not self.call_hook('district_post', district, items): continue
            district.save()
            self.logger.debug("Added district: {}".format(district))
            
    def import_geo_alt_name(self):
        file, uptodate = self.download('alternateNames.zip')[:2]
        if uptodate and not self.options['force']: return
        
        zip = zipfile.ZipFile(file)
        data = zip.read('alternateNames.txt').split('\n')
        zip.close()
        file.close()
        
        self.logger.info("Building geo index")
        geo_index = {}
        for type_ in geo_alt_names:
            for obj in type_.objects.all():
                geo_index[obj.id] = {
                    'type': type_,
                    'object': obj,
                }
        
        self.logger.info("Importing alternate name data")
        for line in data:
            if len(line) < 1 or line[0] == '#': continue
            items = [e.strip() for e in line.split('\t')] 
            if not self.call_hook('alt_name_pre', items): continue
            
            # Only get names for languages in use
            locale = items[2]
            if not locale: locale = 'und'
            if not locale in settings.locales: continue
            
            # Check if known geo id
            geo_id = int(items[1])
            try: geo_info = geo_index[geo_id]
            except: continue
            
            alt_type = geo_alt_names[geo_info['type']][locale]
            alt = alt_type()
            alt.id = int(items[0])
            alt.geo = geo_info['object']
            alt.name = items[3]
            alt.is_preferred = items[4]
            alt.is_short = items[5]
            
            if not self.call_hook('alt_name_post', alt, items): continue
            alt.save()
            self.logger.debug("Added alt name: {}, {} ({})".format(locale, alt, alt.geo))
            
    def import_postal_codes(self):
        file, uptodate = self.download('allCountries.zip')[:2]
        if uptodate and not self.options['force']: return
        
        zip = zipfile.ZipFile(file)
        data = zip.read('allCountries.txt').split('\n')
        zip.close()
        file.close()
        
        self.build_country_index()
        self.build_region_index()
        
        self.logger.info("Building postal code index")
        postal_code_index = defaultdict(dict)
        for country in postal_codes:
            for obj in postal_codes[country].objects.all():
                postal_code_index[country][obj.code] = obj
                
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
            
            # Replace matching postal code in db if any
            try: pc.id = postal_code_index[country_code][code].id
            except: pass
            
            pc.country = country
            pc.code = code
            pc.name = items[2]
            pc.region_0_name = items[3]
            pc.region_1_name = items[5]
            pc.region_2_name = items[7]
            pc.location = Point(float(items[10]), float(items[9]))
            
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
                    self.logger.debug("Postal code: {}: Cannot find region {}: {}".format(pc.code, level+1, code))
            pc.region = region
        
            if not self.call_hook('postal_code_post', pc, items): continue
            pc.save()
            self.logger.debug("Added postal code: {}, {}".format(pc.country, pc))