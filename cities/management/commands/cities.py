"""
GeoNames city data import script.
Requires the following files:

http://download.geonames.org/export/dump/
- Countries:            countryInfo.txt
- Regions:              admin1CodesASCII.txt
- Subregions:           admin2Codes.txt
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
from itertools import chain
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
        
    def parse(self, data):
        for line in data:
            if len(line) < 1 or line[0] == '#': continue
            items = [e.strip() for e in line.split('\t')]
            yield items
            
    def import_country(self):
        uptodate = self.download('country')
        if uptodate and not self.force: return
        data = self.get_data('country')
        
        self.logger.info("Importing country data")
        for items in self.parse(data):
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
        
    def import_region_common(self, region, items):
        class_ = region.__class__
        region.id = int(items[3])
        region.name = items[2]
        region.name_std = items[1]
        region.slug = slugify(region.name)
        region.code = items[0]
        
        # Find country
        country_code = region.code.split('.')[0]
        try: region.country = self.country_index[country_code]
        except:
            self.logger.warning("{}: {}: Cannot find country: {} -- skipping".format(class_.__name__, region.name, country_code))
            return None
            
        return region
    
    def build_country_index(self):
        if hasattr(self, 'country_index'): return
        
        self.logger.info("Building country index")
        self.country_index = {}
        for obj in Country.objects.all():
            self.country_index[obj.code] = obj
            
    def import_region(self):
        uptodate = self.download('region')
        if uptodate and not self.force: return
        data = self.get_data('region')
        
        self.build_country_index()
                
        self.logger.info("Importing region data")
        for items in self.parse(data):
            if not self.call_hook('region_pre', items): continue
            
            region = self.import_region_common(Region(), items)
            if not region: continue
            
            if not self.call_hook('region_post', region, items): continue
            region.save()
            self.logger.debug("Added region: {}, {}".format(region.code, region))
        
    def build_region_index(self):
        if hasattr(self, 'region_index'): return
        
        self.logger.info("Building region index")
        self.region_index = {}
        for obj in chain(Region.objects.all(), Subregion.objects.all()):
            self.region_index[obj.code] = obj
            
    def import_subregion(self):
        uptodate = self.download('subregion')
        if uptodate and not self.force: return
        data = self.get_data('subregion')
        
        self.build_country_index()
        self.build_region_index()
                
        self.logger.info("Importing subregion data")
        for items in self.parse(data):
            if not self.call_hook('subregion_pre', items): continue
            
            subregion = self.import_region_common(Subregion(), items)
            if not subregion: continue
            
            # Find region
            level = Region.levels.index("subregion") - 1
            region_code = '.'.join(subregion.code.split('.')[:level+2])
            try: subregion.region = self.region_index[region_code]
            except:
                self.logger.warning("Subregion: {}: Cannot find region: {}".format(subregion.name, region_code))
                continue
                
            if not self.call_hook('subregion_post', subregion, items): continue
            subregion.save()
            self.logger.debug("Added subregion: {}, {}".format(subregion.code, subregion))
            
        del self.region_index
        
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
        item_offset = 10
        for level, level_name in reversed(list(enumerate(Region.levels))):
            if not items[item_offset+level]: continue
            try:
                code = '.'.join([country_code] + [items[item_offset+i] for i in range(level+1)])
                region = self.region_index[code]
                if class_ is City:
                    setattr(city, level_name, region)
            except:
                self.logger.log(logging.DEBUG if level else logging.WARNING, # Escalate if level 0 failed
                                "{}: {}: Cannot find {}: {}".format(class_.__name__, city.name, level_name, code))
        
        
        return city
            
    def import_city(self):            
        uptodate = self.download_once('city')
        if uptodate and not self.force: return
        data = self.get_data('city')
        
        self.build_country_index()
        self.build_region_index()

        self.logger.info("Importing city data")
        for items in self.parse(data):
            if not self.call_hook('city_pre', items): continue
            
            type = items[7]
            if type not in city_types: continue
            
            city = self.import_city_common(City(), items)
            if not city: continue
            
            if not self.call_hook('city_post', city, items): continue
            city.save()
            self.logger.debug("Added city: {}".format(city))
        
    def build_hierarchy(self):
        if hasattr(self, 'hierarchy'): return
        
        self.download('hierarchy')
        data = self.get_data('hierarchy')
        
        self.logger.info("Building hierarchy index")
        self.hierarchy = {}
        for items in self.parse(data):
            parent_id = int(items[0])
            child_id = int(items[1])
            self.hierarchy[child_id] = parent_id
            
    def import_district(self):
        uptodate = self.download_once('city')
        if uptodate and not self.force: return
        data = self.get_data('city')
        
        self.build_country_index()
        self.build_region_index()
        self.build_hierarchy()
            
        self.logger.info("Building city index")
        city_index = {}
        for obj in City.objects.all():
            city_index[obj.id] = obj
            
        self.logger.info("Importing district data")
        for items in self.parse(data):
            if not self.call_hook('district_pre', items): continue
            
            type = items[7]
            if type not in district_types: continue
            
            district = self.import_city_common(District(), items)
            if not district: continue
            
            # Find city
            city = None
            try: city = city_index[self.hierarchy[district.id]]
            except:
                self.logger.warning("District: {}: Cannot find city in hierarchy, using nearest".format(district.name))
                city_pop_min = 100000
                if connection.ops.mysql:
                    # mysql doesn't have distance function, get nearest city within 2 degrees
                    search_deg = 2
                    min_dist = float('inf')
                    bounds = Envelope(  district.location.x-search_deg, district.location.y-search_deg,
                                        district.location.x+search_deg, district.location.y+search_deg)
                    for e in City.objects.filter(population__gt=city_pop_min).filter(location__intersects=bounds.wkt):
                        dist = geo_distance(district.location, e.location)
                        if dist < min_dist:
                            min_dist = dist
                            city = e
                else:
                    city = City.objects.filter(population__gt=city_pop_min).distance(district.location).order_by('distance')[0]
            if not city:
                self.logger.warning("District: {}: Cannot find city -- skipping".format(district.name))
                continue
            district.city = city
            
            if not self.call_hook('district_post', district, items): continue
            district.save()
            self.logger.debug("Added district: {}".format(district))
        
    def import_alt_name(self):
        uptodate = self.download('alt_name')
        if uptodate and not self.force: return
        data = self.get_data('alt_name')
        
        self.logger.info("Building geo index")
        geo_index = {}
        for type_ in geo_alt_names:
            for obj in type_.objects.all():
                geo_index[obj.id] = {
                    'type': type_,
                    'object': obj,
                }
        
        self.logger.info("Importing alternate name data")
        for items in self.parse(data):
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
            
    def import_postal_code(self):
        uptodate = self.download('postal_code')
        if uptodate and not self.force: return
        data = self.get_data('postal_code')
        
        self.build_country_index()
        self.build_region_index()
                
        self.logger.info("Importing postal codes")
        for items in self.parse(data):
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
            pc.region_name = items[3]
            pc.subregion_name = items[5]
            pc.district_name = items[7]
            
            try: pc.location = Point(float(items[10]), float(items[9]))
            except:
                self.logger.warning("Postal code: {}, {}: Invalid location ({}, {})".format(pc.country, pc.code, items[10], items[9]))
                pc.location = Point(0,0)
                
            # Find region, search highest level first
            item_offset = 4
            for level, level_name in reversed(list(enumerate(Region.levels))):
                if not items[item_offset+level*2]: continue
                try:
                    code = '.'.join([country_code] + [items[item_offset+i*2] for i in range(level+1)])
                    region = self.region_index[code]
                    setattr(pc, level_name, region)
                except:
                    self.logger.log(logging.DEBUG if level else logging.WARNING, # Escalate if level 0 failed
                                    "Postal code: {}, {}: Cannot find {}: {}".format(pc.country, pc.code, level_name, code))
        
            if not self.call_hook('postal_code_post', pc, items): continue
            pc.save()
            self.logger.debug("Added postal code: {}, {}".format(pc.country, pc))
            
    def flush_country(self):
        self.logger.info("Flushing country data")
        Country.objects.all().delete()
        
    def flush_region(self):
        self.logger.info("Flushing region data")
        Region.objects.all().delete()
        
    def flush_subregion(self):
        self.logger.info("Flushing subregion data")
        Subregion.objects.all().delete()
        
    def flush_city(self):
        self.logger.info("Flushing city data")
        City.objects.all().delete()
    
    def flush_district(self):
        self.logger.info("Flushing district data")
        District.objects.all().delete()
    
    def flush_alt_name(self):
        self.logger.info("Flushing alternate name data")
        [geo_alt_name.objects.all().delete() for locales in geo_alt_names.values() for geo_alt_name in locales.values()]
        
    def flush_postal_code(self):
        self.logger.info("Flushing postal code data")
        [postal_code.objects.all().delete() for postal_code in postal_codes.values()]
    