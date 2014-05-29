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
from itertools import chain
from optparse import make_option
from django.core.management.base import BaseCommand
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
        if hasattr(settings, 'plugins'):
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
            self.logger.error("Web file not found: {0}. Tried URLs:\n{1}".format(filename, '\n'.join(urls)))
            
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
        name, ext = filename.rsplit('.', 1)
        if (ext == 'zip'):
            file = zipfile.ZipFile(file).open(name + '.txt')

        data = (
            dict(zip(settings.files[filekey]['fields'], row.split("\t"))) 
            for row in file if not row.startswith('#')
        )

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

        neighbours = {}
        countries = {}

        self.logger.info("Importing country data")
        for item in data:
            self.logger.info(item)
            if not self.call_hook('country_pre', item): continue
            
            country = Country()
            try: country.id = int(item['geonameid'])
            except: 
                continue

            country.name = item['name']
            country.slug = slugify(country.name)
            country.code = item['code']
            country.code3 = item['code3']
            country.population = item['population']
            country.continent = item['continent']
            country.tld = item['tld'][1:] # strip the leading .
            country.phone = item['phone']
            country.currency = item['currencyCode']
            country.currency_name = item['currencyName']
            country.capital = item['capital']
            country.area = int(float(item['area'])) if item['area'] else None
            country.languages = item['languages']

            neighbours[country] = item['neighbours'].split(",")
            countries[country.code] = country
            
            if not self.call_hook('country_post', country, item): continue 
            country.save()

        for country, neighbour_codes in neighbours.items():
            neighbours = [x for x in [countries.get(x) for x in neighbour_codes if x] if x]
            country.neighbours.add(*neighbours)
        
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
        for item in data:
            if not self.call_hook('region_pre', item): continue
            
            region = Region()

            region.id = int(item['geonameid'])
            region.name = item['name']
            region.name_std = item['asciiName']
            region.slug = slugify(region.name_std)

            country_code, region_code = item['code'].split(".")
            region.code = region_code
            try: 
                region.country = self.country_index[country_code]
            except:
                self.logger.warning("{0}: {1}: Cannot find country: {2} -- skipping".format(class_.__name__, region.name, country_code))
                continue
            
            if not self.call_hook('region_post', region, item): continue
            region.save()
            self.logger.debug("Added region: {0}, {1}".format(item['code'], region))
        
    def build_region_index(self):
        if hasattr(self, 'region_index'): return
        
        self.logger.info("Building region index")
        self.region_index = {}
        for obj in chain(Region.objects.all(), Subregion.objects.all()):
            self.region_index[obj.full_code()] = obj
            
    def import_subregion(self):
        uptodate = self.download('subregion')
        if uptodate and not self.force: return

        data = self.get_data('subregion')
        
        self.build_country_index()
        self.build_region_index()
                
        self.logger.info("Importing subregion data")
        for item in data:
            if not self.call_hook('subregion_pre', item): continue
            
            subregion = Subregion()

            subregion.id = int(item['geonameid'])
            subregion.name = item['name']
            subregion.name_std = item['asciiName']
            subregion.slug = slugify(subregion.name_std)

            country_code, region_code, subregion_code = item['code'].split(".")
            subregion.code = subregion_code
            try: 
                subregion.region = self.region_index[country_code + "." + region_code]
            except:
                self.logger.warning("Subregion: {0}: Cannot find region: {1}".format(subregion.name, region_code))
                continue
                
            if not self.call_hook('subregion_post', subregion, item): continue
            subregion.save()
            self.logger.debug("Added subregion: {0}, {1}".format(item['code'], subregion))
            
        del self.region_index
        
    def import_city(self):            
        uptodate = self.download_once('city')
        if uptodate and not self.force: return
        data = self.get_data('city')

        self.build_country_index()
        self.build_region_index()

        self.logger.info("Importing city data")
        for item in data:
            if not self.call_hook('city_pre', item): continue
            
            if item['featureCode'] not in city_types: continue

            city = City()
            try:
                city.id = int(item['geonameid'])
            except:
                continue
            city.name = item['name']
            city.kind = item['featureCode']
            city.name_std = item['asciiName']
            city.slug = slugify(city.name_std)
            city.location = Point(float(item['longitude']), float(item['latitude']))
            city.population = int(item['population'])
            city.timezone = item['timezone']
            try:
                city.elevation = int(item['elevation'])
            except:
                pass

            country_code = item['countryCode']
            try: 
                country = self.country_index[country_code]
                city.country = country
            except:
                self.logger.warning("{0}: {1}: Cannot find country: {2} -- skipping".format("CITY", city.name, country_code))
                continue

            region_code = item['admin1Code']
            try: 
                region = self.region_index[country_code + "." + region_code]
                city.region = region
            except:
                self.logger.warning("{0}: {1}: Cannot find region: {2} -- skipping".format(country_code, city.name, region_code))
                continue
            
            subregion_code = item['admin2Code']
            try: 
                subregion = self.region_index[country_code + "." + region_code + "." + subregion_code]
                city.subregion = subregion
            except:
                if subregion_code:
                    self.logger.warning("{0}: {1}: Cannot find subregion: {2} -- skipping".format(country_code, city.name, subregion_code))
                pass
            
            if not self.call_hook('city_post', city, item): continue
            city.save()
            self.logger.debug("Added city: {0}".format(city))
        
    def build_hierarchy(self):
        if hasattr(self, 'hierarchy'): return
        
        self.download('hierarchy')
        data = self.get_data('hierarchy')
        
        self.logger.info("Building hierarchy index")
        self.hierarchy = {}
        for item in data:
            parent_id = int(item['parent'])
            child_id = int(item['child'])
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
        for item in data:
            if not self.call_hook('district_pre', item): continue
            
            type = item['featureCode']
            if type not in district_types: continue
            
            district = District()
            district.name = item['name']
            district.name_std = item['asciiName']
            district.slug = slugify(district.name_std)
            district.location = Point(float(item['longitude']), float(item['latitude']))
            district.population = int(item['population'])
            
            # Find city
            city = None
            try: 
                city = city_index[self.hierarchy[district.id]]
            except:
                self.logger.warning("District: {0}: Cannot find city in hierarchy, using nearest".format(district.name))
                city_pop_min = 100000
                # we are going to try to find closet city using native database .distance(...) query but if that fails
                # then we fall back to degree search, MYSQL has no support and Spatialite with SRID 4236. 
                try:
                    city = City.objects.filter(population__gt=city_pop_min).distance(district.location).order_by('distance')[0]
                except:
                    self.logger.warning("District: {0}: DB backend does not support native '.distance(...)' query " \
                                        "falling back to two degree search".format(district.name))
                    search_deg = 2
                    min_dist = float('inf')
                    bounds = Envelope(district.location.x-search_deg, district.location.y-search_deg,
                                      district.location.x+search_deg, district.location.y+search_deg)
                    for e in City.objects.filter(population__gt=city_pop_min).filter(location__intersects=bounds.wkt):
                        dist = geo_distance(district.location, e.location)
                        if dist < min_dist:
                            min_dist = dist
                            city = e
                    
            if not city:
                self.logger.warning("District: {0}: Cannot find city -- skipping".format(district.name))
                continue

            district.city = city
            
            if not self.call_hook('district_post', district, item): continue
            district.save()
            self.logger.debug("Added district: {0}".format(district))
        
    def import_alt_name(self):
        uptodate = self.download('alt_name')
        if uptodate and not self.force: return
        data = self.get_data('alt_name')
        
        self.logger.info("Building geo index")
        geo_index = {}
        for type_ in [Country, Region, Subregion, City, District]:
            for obj in type_.objects.all():
                geo_index[obj.id] = {
                    'type': type_,
                    'object': obj,
                }
        
        self.logger.info("Importing alternate name data")
        for item in data:
            if not self.call_hook('alt_name_pre', item): continue
            
            # Only get names for languages in use
            locale = item['language']
            if not locale: locale = 'und'
            if not locale in settings.locales and 'all' not in settings.locales: 
                self.logger.info("SKIPPING {0}".format(settings.locales))
                continue
            
            # Check if known geo id
            geo_id = int(item['geonameid'])
            try: geo_info = geo_index[geo_id]
            except: continue
            
            alt = AlternativeName()
            alt.id = int(item['nameid'])
            alt.name = item['name']
            alt.is_preferred = item['isPreferred']
            alt.is_short = item['isShort']
            alt.language = locale

            if not self.call_hook('alt_name_post', alt, item): continue
            alt.save()
            geo_info['object'].alt_names.add(alt)

            self.logger.debug("Added alt name: {0}, {1}".format(locale, alt))

    def import_postal_code(self):
        uptodate = self.download('postal_code')
        if uptodate and not self.force: return
        data = self.get_data('postal_code')

        self.build_country_index()
        self.build_region_index()

        self.logger.info("Importing postal codes")
        for item in data:
            if not self.call_hook('postal_code_pre', item): continue

            country_code = item['countryCode']
            if country_code not in settings.postal_codes and 'ALL' not in settings.postal_codes: continue

            # Find country
            code = item['postalCode']
            country = None
            try:
                country = self.country_index[country_code]
            except:
                self.logger.warning("Postal code: {0}: Cannot find country: {1} -- skipping".format(code, country_code))
                continue

            pc = PostalCode()
            pc.country = country
            pc.code = code
            pc.name = item['placeName']
            pc.region_name = item['admin1Name']
            pc.subregion_name = item['admin2Name']
            pc.district_name = item['admin3Name']

            try:
                pc.location = Point(float(item['longitude']), float(item['latitude']))
            except:
                self.logger.warning("Postal code: {0}, {1}: Invalid location ({2}, {3})".format(pc.country, pc.code, item['longitude'], item['latitude']))
                continue

            if not self.call_hook('postal_code_post', pc, item): continue
            self.logger.debug("Adding postal code: {0}, {1}".format(pc.country, pc))
            try:
                pc.save()
            except Exception, e:
                print e

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
        AlternativeName.objects.all().delete()
        
    def flush_postal_code(self):
        self.logger.info("Flushing postal code data")
        PostalCode.objects.all().delete()
