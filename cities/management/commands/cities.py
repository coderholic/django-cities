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

from __future__ import print_function

import io
import json
import logging
import math
import os
import re
import sys
import zipfile

try:
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen

from itertools import chain
from optparse import make_option
from swapper import load_model
from tqdm import tqdm

from django import VERSION as django_version
from django.contrib.gis.gdal.envelope import Envelope
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
try:
    from django.contrib.gis.db.models.functions import Distance
except ImportError:
    pass
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q
from django.db.models import CharField, ForeignKey

from ...conf import (city_types, district_types, import_opts, import_opts_all,
                     HookException, settings, CURRENCY_SYMBOLS,
                     INCLUDE_AIRPORT_CODES, INCLUDE_NUMERIC_ALTERNATIVE_NAMES,
                     NO_LONGER_EXISTENT_COUNTRY_CODES,
                     SKIP_CITIES_WITH_EMPTY_REGIONS, VALIDATE_POSTAL_CODES)
from ...models import (Region, Subregion, District, PostalCode, AlternativeName)
from ...util import geo_distance


# Interpret all files as utf-8
if sys.version_info < (3,):
    reload(sys)  # noqa: F821
    sys.setdefaultencoding('utf-8')

# Load swappable models
Continent = load_model('cities', 'Continent')
Country = load_model('cities', 'Country')
City = load_model('cities', 'City')


# Only log errors during Travis tests
LOGGER_NAME = os.environ.get('TRAVIS_LOGGER_NAME', 'cities')

# TODO: Remove backwards compatibility once django-cities requires Django 1.7
# or 1.8 LTS.
# _transact = (transaction.commit_on_success if django_version < (1, 6) else
#              transaction.atomic)


class Command(BaseCommand):
    if hasattr(settings, 'data_dir'):
        data_dir = settings.data_dir
    else:
        app_dir = os.path.normpath(os.path.dirname(os.path.realpath(__file__)) + '/../..')
        data_dir = os.path.join(app_dir, 'data')
    logger = logging.getLogger(LOGGER_NAME)

    if django_version < (1, 8):
        option_list = getattr(BaseCommand, 'option_list', ()) + (
            make_option(
                '--force',
                action='store_true',
                default=False,
                help='Import even if files are up-to-date.'),
            make_option(
                '--import',
                metavar="DATA_TYPES",
                default='all',
                help='Selectively import data. Comma separated list of data ' +
                     'types: ' + str(import_opts).replace("'", '')),
            make_option(
                '--flush',
                metavar="DATA_TYPES",
                default='',
                help="Selectively flush data. Comma separated list of data types."),
        )

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            default=False,
            dest="force",
            help='Import even if files are up-to-date.'
        )
        parser.add_argument(
            '--import',
            metavar="DATA_TYPES",
            default='all',
            dest="import",
            help='Selectively import data. Comma separated list of data '
                 'types: ' + str(import_opts).replace("'", '')
        )
        parser.add_argument(
            '--flush',
            metavar="DATA_TYPES",
            default='',
            dest="flush",
            help="Selectively flush data. Comma separated list of data types."
        )
        parser.add_argument(
            '--quiet',
            action='store_true',
            default=False,
            dest="quiet",
            help="Do not show the progress bar."
        )

    @transaction.atomic
    def handle(self, *args, **options):
        self.download_cache = {}
        self.options = options

        self.force = self.options['force']

        self.flushes = [e for e in self.options.get('flush', '').split(',') if e]
        if 'all' in self.flushes:
            self.flushes = import_opts_all
        for flush in self.flushes:
            func = getattr(self, "flush_" + flush)
            func()

        self.imports = [e for e in self.options.get('import', '').split(',') if e]
        if 'all' in self.imports:
            self.imports = import_opts_all
        if self.flushes:
            self.imports = []
        for import_ in self.imports:
            func = getattr(self, "import_" + import_)
            func()

    def call_hook(self, hook, *args, **kwargs):
        if hasattr(settings, 'plugins'):
            for plugin in settings.plugins[hook]:
                try:
                    func = getattr(plugin, hook)
                    func(self, *args, **kwargs)
                except HookException as e:
                    error = str(e)
                    if error:
                        self.logger.error(error)
                    return False
        return True

    def download(self, filekey):
        if 'filename' in settings.files[filekey]:
            filenames = [settings.files[filekey]['filename']]
        else:
            filenames = settings.files[filekey]['filenames']

        for filename in filenames:
            web_file = None
            urls = [e.format(filename=filename) for e in settings.files[filekey]['urls']]
            for url in urls:
                try:
                    web_file = urlopen(url)
                    if 'html' in web_file.headers['Content-Type']:
                        # TODO: Make this a subclass
                        raise Exception("Content type of downloaded file was {}".format(web_file.headers['Content-Type']))
                    self.logger.debug("Downloaded: {}".format(url))
                    break
                except Exception:
                    web_file = None
                    continue
            else:
                self.logger.error("Web file not found: %s. Tried URLs:\n%s", filename, '\n'.join(urls))

            if web_file is not None:
                self.logger.debug("Saving: {}/{}".format(self.data_dir, filename))
                if not os.path.exists(self.data_dir):
                    os.makedirs(self.data_dir)
                file = io.open(os.path.join(self.data_dir, filename), 'wb')
                file.write(web_file.read())
                file.close()
            elif not os.path.exists(os.path.join(self.data_dir, filename)):
                raise Exception("File not found and download failed: {} [{}]".format(filename, url))

    def get_data(self, filekey):
        if 'filename' in settings.files[filekey]:
            filenames = [settings.files[filekey]['filename']]
        else:
            filenames = settings.files[filekey]['filenames']

        for filename in filenames:
            name, ext = filename.rsplit('.', 1)
            if (ext == 'zip'):
                filepath = os.path.join(self.data_dir, filename)
                zip_member = zipfile.ZipFile(filepath).open(name + '.txt', 'r')
                file_obj = io.TextIOWrapper(zip_member, encoding='utf-8')
            else:
                file_obj = io.open(os.path.join(self.data_dir, filename),
                                   'r', encoding='utf-8')

            for row in file_obj:
                if not row.startswith('#'):
                    yield dict(list(zip(settings.files[filekey]['fields'],
                                        row.rstrip('\n').split("\t"))))

    def parse(self, data):
        for line in data:
            if len(line) < 1 or line[0] == '#':
                continue
            items = [e.strip() for e in line.split('\t')]
            yield items

    def import_country(self):
        self.download('country')
        data = self.get_data('country')

        total = sum(1 for _ in data) - len(NO_LONGER_EXISTENT_COUNTRY_CODES)

        data = self.get_data('country')

        neighbours = {}
        countries = {}

        continents = {c.code: c for c in Continent.objects.all()}

        # If the continent attribute on Country is a ForeignKey, import
        # continents as ForeignKeys to the Continent models, otherwise assume
        # they are still the CharField(max_length=2) and import them the old way
        import_continents_as_fks = type(Country._meta.get_field('continent')) == ForeignKey

        for item in tqdm([d for d in data if d['code'] not in NO_LONGER_EXISTENT_COUNTRY_CODES],
                         disable=self.options.get('quiet'),
                         total=total,
                         desc="Importing countries"):
            if not self.call_hook('country_pre', item):
                continue

            try:
                country_id = int(item['geonameid'])
            except KeyError:
                self.logger.warning("Country has no geonameid: {} -- skipping".format(item))
                continue
            except ValueError:
                self.logger.warning("Country has non-numeric geonameid: {} -- skipping".format(item['geonameid']))
                continue

            defaults = {
                'name': item['name'],
                'code': item['code'],
                'code3': item['code3'],
                'population': item['population'],
                'continent': continents[item['continent']] if import_continents_as_fks else item['continent'],
                'tld': item['tld'][1:],  # strip the leading .
                'phone': item['phone'],
                'currency': item['currencyCode'],
                'currency_name': item['currencyName'],
                'capital': item['capital'],
                'area': int(float(item['area'])) if item['area'] else None,
            }

            if hasattr(Country, 'language_codes'):
                defaults['language_codes'] = item['languages']
            elif hasattr(Country, 'languages') and type(getattr(Country, 'languages')) == CharField:
                defaults['languages'] = item['languages']

            # These fields shouldn't impact saving older models (that don't
            # have these attributes)
            try:
                defaults['currency_symbol'] = CURRENCY_SYMBOLS.get(item['currencyCode'], None)
                defaults['postal_code_format'] = item['postalCodeFormat']
                defaults['postal_code_regex'] = item['postalCodeRegex']
            except AttributeError:
                pass

            # Make importing countries idempotent
            country, created = Country.objects.update_or_create(id=country_id, defaults=defaults)

            self.logger.debug("%s country '%s'",
                              "Added" if created else "Updated",
                              defaults['name'])

            neighbours[country] = item['neighbours'].split(",")
            countries[country.code] = country

            if not self.call_hook('country_post', country, item):
                continue

        for country, neighbour_codes in tqdm(list(neighbours.items()),
                                             disable=self.options.get('quiet'),
                                             total=len(neighbours),
                                             desc="Importing country neighbours"):
            neighbours = [x for x in [countries.get(x) for x in neighbour_codes if x] if x]
            country.neighbours.add(*neighbours)

    def build_country_index(self):
        if hasattr(self, 'country_index'):
            return

        self.country_index = {}
        for obj in tqdm(Country.objects.all(),
                        disable=self.options.get('quiet'),
                        total=Country.objects.all().count(),
                        desc="Building country index"):
            self.country_index[obj.code] = obj

    def import_region(self):
        self.download('region')
        data = self.get_data('region')

        self.build_country_index()

        total = sum(1 for _ in data)

        data = self.get_data('region')

        countries_not_found = {}
        for item in tqdm(data, disable=self.options.get('quiet'), total=total, desc="Importing regions"):
            if not self.call_hook('region_pre', item):
                continue

            try:
                region_id = int(item['geonameid'])
            except KeyError:
                self.logger.warning("Region has no geonameid: {} -- skipping".format(item))
                continue
            except ValueError:
                self.logger.warning("Region has non-numeric geonameid: {} -- skipping".format(item['geonameid']))
                continue

            country_code, region_code = item['code'].split(".")

            defaults = {
                'name': item['name'],
                'name_std': item['asciiName'],
                'code': region_code,
            }

            try:
                defaults['country'] = self.country_index[country_code]
            except KeyError:
                countries_not_found.setdefault(country_code, []).append(defaults['name'])
                self.logger.warning("Region: %s: Cannot find country: %s -- skipping",
                                    defaults['name'], country_code)
                continue

            region, created = Region.objects.update_or_create(id=region_id, defaults=defaults)

            if not self.call_hook('region_post', region, item):
                continue

            self.logger.debug("%s region: %s, %s",
                              "Added" if created else "Updated",
                              item['code'], region)

        if countries_not_found:
            countries_not_found_file = os.path.join(self.data_dir, 'countries_not_found.json')
            try:
                with open(countries_not_found_file, 'w+') as fp:
                    json.dump(countries_not_found, fp)
            except Exception as e:
                self.logger.warning("Unable to write log file '{}': {}".format(
                                    countries_not_found_file, e))

    def build_region_index(self):
        if hasattr(self, 'region_index'):
            return

        self.region_index = {}
        for obj in tqdm(chain(Region.objects.all().prefetch_related('country'),
                              Subregion.objects.all().prefetch_related('region__country')),
                        disable=self.options.get('quiet'),
                        total=Region.objects.all().count() + Subregion.objects.all().count(),
                        desc="Building region index"):
            self.region_index[obj.full_code()] = obj

    def import_subregion(self):
        self.download('subregion')
        data = self.get_data('subregion')

        total = sum(1 for _ in data)

        data = self.get_data('subregion')

        self.build_country_index()
        self.build_region_index()

        regions_not_found = {}
        for item in tqdm(data, disable=self.options.get('quiet'), total=total, desc="Importing subregions"):
            if not self.call_hook('subregion_pre', item):
                continue

            try:
                subregion_id = int(item['geonameid'])
            except KeyError:
                self.logger.warning("Subregion has no geonameid: {} -- skipping".format(item))
                continue
            except ValueError:
                self.logger.warning("Subregion has non-numeric geonameid: {} -- skipping".format(item['geonameid']))
                continue

            country_code, region_code, subregion_code = item['code'].split(".")

            defaults = {
                'name': item['name'],
                'name_std': item['asciiName'],
                'code': subregion_code,
            }

            try:
                defaults['region'] = self.region_index[country_code + "." + region_code]
            except KeyError:
                regions_not_found.setdefault(country_code, {})
                regions_not_found[country_code].setdefault(region_code, []).append(defaults['name'])
                self.logger.debug("Subregion: %s %s: Cannot find region",
                                  item['code'], defaults['name'])
                continue

            subregion, created = Subregion.objects.update_or_create(id=subregion_id, defaults=defaults)

            if not self.call_hook('subregion_post', subregion, item):
                continue

            self.logger.debug("%s subregion: %s, %s",
                              "Added" if created else "Updated",
                              item['code'], subregion)

        if regions_not_found:
            regions_not_found_file = os.path.join(self.data_dir, 'regions_not_found.json')
            try:
                with open(regions_not_found_file, 'w+') as fp:
                    json.dump(regions_not_found, fp)
            except Exception as e:
                self.logger.warning("Unable to write log file '{}': {}".format(
                                    regions_not_found_file, e))

        del self.region_index

    def import_city(self):
        self.download('city')
        data = self.get_data('city')

        total = sum(1 for _ in data)

        data = self.get_data('city')

        self.build_country_index()
        self.build_region_index()

        for item in tqdm(data, disable=self.options.get('quiet'), total=total, desc="Importing cities"):
            if not self.call_hook('city_pre', item):
                continue

            if item['featureCode'] not in city_types:
                continue

            try:
                city_id = int(item['geonameid'])
            except KeyError:
                self.logger.warning("City has no geonameid: {} -- skipping".format(item))
                continue
            except ValueError:
                self.logger.warning("City has non-numeric geonameid: {} -- skipping".format(item['geonameid']))
                continue

            defaults = {
                'name': item['name'],
                'kind': item['featureCode'],
                'name_std': item['asciiName'],
                'location': Point(float(item['longitude']), float(item['latitude'])),
                'population': int(item['population']),
                'timezone': item['timezone'],
            }

            try:
                defaults['elevation'] = int(item['elevation'])
            except (KeyError, ValueError):
                pass

            country_code = item['countryCode']
            try:
                country = self.country_index[country_code]
                defaults['country'] = country
            except KeyError:
                self.logger.warning("City: %s: Cannot find country: '%s' -- skipping",
                                    item['name'], country_code)
                continue

            region_code = item['admin1Code']
            try:
                region_key = country_code + "." + region_code
                region = self.region_index[region_key]
                defaults['region'] = region
            except KeyError:
                self.logger.debug('SKIP_CITIES_WITH_EMPTY_REGIONS: %s', str(SKIP_CITIES_WITH_EMPTY_REGIONS))
                if SKIP_CITIES_WITH_EMPTY_REGIONS:
                    self.logger.debug("%s: %s: Cannot find region: '%s' -- skipping",
                                      country_code, item['name'], region_code)
                    continue
                else:
                    defaults['region'] = None

            subregion_code = item['admin2Code']
            try:
                subregion = self.region_index[country_code + "." + region_code + "." + subregion_code]
                defaults['subregion'] = subregion
            except KeyError:
                try:
                    with transaction.atomic():
                        defaults['subregion'] = Subregion.objects.get(
                            Q(name=subregion_code) |
                            Q(name=subregion_code.replace(' (undefined)', '')),
                            region=defaults['region'])
                except Subregion.DoesNotExist:
                    try:
                        with transaction.atomic():
                            defaults['subregion'] = Subregion.objects.get(
                                Q(name_std=subregion_code) |
                                Q(name_std=subregion_code.replace(' (undefined)', '')),
                                region=defaults['region'])
                    except Subregion.DoesNotExist:
                        if subregion_code:
                            self.logger.debug("%s: %s: Cannot find subregion: '%s'",
                                              country_code, item['name'], subregion_code)
                        defaults['subregion'] = None

            city, created = City.objects.update_or_create(id=city_id, defaults=defaults)

            if not self.call_hook('city_post', city, item):
                continue

            self.logger.debug("%s city: %s",
                              "Added" if created else "Updated", city)

    def build_hierarchy(self):
        if hasattr(self, 'hierarchy') and self.hierarchy:
            return

        self.download('hierarchy')
        data = self.get_data('hierarchy')

        total = sum(1 for _ in data)

        data = self.get_data('hierarchy')

        self.hierarchy = {}
        for item in tqdm(data, disable=self.options.get('quiet'), total=total, desc="Building hierarchy index"):
            parent_id = int(item['parent'])
            child_id = int(item['child'])
            self.hierarchy[child_id] = parent_id

    def import_district(self):
        self.download('city')
        data = self.get_data('city')

        total = sum(1 for _ in data)

        data = self.get_data('city')

        self.build_country_index()
        self.build_region_index()
        self.build_hierarchy()

        city_index = {}
        for obj in tqdm(City.objects.all(),
                        disable=self.options.get('quiet'),
                        total=City.objects.all().count(),
                        desc="Building city index"):
            city_index[obj.id] = obj

        for item in tqdm(data, disable=self.options.get('quiet'), total=total, desc="Importing districts"):
            if not self.call_hook('district_pre', item):
                continue

            _type = item['featureCode']
            if _type not in district_types:
                continue

            defaults = {
                'name': item['name'],
                'name_std': item['asciiName'],
                'location': Point(float(item['longitude']), float(item['latitude'])),
                'population': int(item['population']),
            }

            if hasattr(District, 'code'):
                defaults['code'] = item['admin3Code'],

            geonameid = int(item['geonameid'])

            # Find city
            city = None
            try:
                city = city_index[self.hierarchy[geonameid]]
            except KeyError:
                self.logger.debug("District: %d %s: Cannot find city in hierarchy, using nearest", geonameid, defaults['name'])
                city_pop_min = 100000
                # we are going to try to find closet city using native
                # database .distance(...) query but if that fails then
                # we fall back to degree search, MYSQL has no support
                # and Spatialite with SRID 4236.
                try:
                    if django_version < (1, 9):
                        city = City.objects.filter(population__gt=city_pop_min)\
                                   .distance(defaults['location'])\
                                   .order_by('distance')[0]
                    else:
                        city = City.objects.filter(
                            location__distance_lte=(defaults['location'], D(km=1000))
                        ).annotate(
                            distance=Distance('location', defaults['location'])
                        ).order_by('distance').first()
                except City.DoesNotExist as e:
                    self.logger.warning(
                        "District: %s: DB backend does not support native '.distance(...)' query "
                        "falling back to two degree search",
                        defaults['name']
                    )
                    search_deg = 2
                    min_dist = float('inf')
                    bounds = Envelope(
                        defaults['location'].x - search_deg, defaults['location'].y - search_deg,
                        defaults['location'].x + search_deg, defaults['location'].y + search_deg)
                    for e in City.objects.filter(population__gt=city_pop_min).filter(
                            location__intersects=bounds.wkt):
                        dist = geo_distance(defaults['location'], e.location)
                        if dist < min_dist:
                            min_dist = dist
                            city = e
            else:
                self.logger.debug("Found city in hierarchy: %s [%d]", city.name, geonameid)

            if not city:
                self.logger.warning("District: %s: Cannot find city -- skipping", defaults['name'])
                continue

            defaults['city'] = city

            try:
                with transaction.atomic():
                    district = District.objects.get(city=defaults['city'], name=defaults['name'])
            except District.DoesNotExist:
                # If the district doesn't exist, create it with the geonameid
                # as its id
                district, created = District.objects.update_or_create(id=item['geonameid'], defaults=defaults)
            else:
                # Since the district already exists, but doesn't have its
                # geonameid as its id, we need to update all of its attributes
                # *except* for its id
                for key, value in defaults.items():
                    setattr(district, key, value)
                district.save()
                created = False

            if not self.call_hook('district_post', district, item):
                continue

            self.logger.debug("%s district: %s", "Added" if created else "Updated", district)

    def import_alt_name(self):
        self.download('alt_name')
        data = self.get_data('alt_name')

        total = sum(1 for _ in data)

        data = self.get_data('alt_name')

        geo_index = {}
        for type_ in (Country, Region, Subregion, City, District):
            plural_type_name = '{}s'.format(type_.__name__) if type_.__name__[-1] != 'y' else '{}ies'.format(type_.__name__[:-1])
            for obj in tqdm(type_.objects.all(),
                            disable=self.options.get('quiet'),
                            total=type_.objects.all().count(),
                            desc="Building geo index for {}".format(plural_type_name.lower())):
                geo_index[obj.id] = {
                    'type': type_,
                    'object': obj,
                }

        for item in tqdm(data, disable=self.options.get('quiet'), total=total, desc="Importing data for alternative names"):
            if not self.call_hook('alt_name_pre', item):
                continue

            # Only get names for languages in use
            locale = item['language']
            if not locale:
                locale = 'und'
            if locale not in settings.locales and 'all' not in settings.locales:
                self.logger.debug(
                    "Alternative name with language [{}]: {} "
                    "({}) -- skipping".format(
                        item['language'], item['name'], item['nameid']))
                continue

            # Check if known geo id
            geo_id = int(item['geonameid'])
            try:
                geo_info = geo_index[geo_id]
            except KeyError:
                continue

            try:
                alt_id = int(item['nameid'])
            except KeyError:
                self.logger.warning("Alternative name has no nameid: {} -- skipping".format(item))
                continue

            try:
                alt = AlternativeName.objects.get(id=alt_id)
            except AlternativeName.DoesNotExist:
                alt = AlternativeName(id=alt_id)

            alt.name = item['name']
            alt.is_preferred = bool(item['isPreferred'])
            alt.is_short = bool(item['isShort'])
            try:
                alt.language_code = locale
            except AttributeError:
                alt.language = locale

            try:
                int(item['name'])
            except ValueError:
                pass
            else:
                if not INCLUDE_NUMERIC_ALTERNATIVE_NAMES:
                    self.logger.debug(
                        "Trying to add a numeric alternative name to {} ({}): {} -- skipping".format(
                            geo_info['object'].name,
                            geo_info['type'].__name__,
                            item['name']))
                    continue
            alt.is_historic = True if ((item['isHistoric'] and
                                        item['isHistoric'] != '\n') or
                                       locale == 'fr_1793') else False

            if locale == 'post':
                try:
                    if geo_index[item['geonameid']]['type'] == Region:
                        region = geo_index[item['geonameid']]['object']
                        PostalCode.objects.get_or_create(
                            code=item['name'],
                            country=region.country,
                            region=region,
                            region_name=region.name)
                    elif geo_index[item['geonameid']]['type'] == Subregion:
                        subregion = geo_index[item['geonameid']]['object']
                        PostalCode.objects.get_or_create(
                            code=item['name'],
                            country=subregion.region.country,
                            region=subregion.region,
                            subregion=subregion,
                            region_name=subregion.region.name,
                            subregion_name=subregion.name)
                    elif geo_index[item['geonameid']]['type'] == City:
                        city = geo_index[item['geonameid']]['object']
                        PostalCode.objects.get_or_create(
                            code=item['name'],
                            country=city.country,
                            region=city.region,
                            subregion=city.subregion,
                            region_name=city.region.name,
                            subregion_name=city.subregion.name)
                except KeyError:
                    pass

                continue

            if hasattr(alt, 'kind'):
                if locale in ('abbr', 'link', 'name') or \
                   INCLUDE_AIRPORT_CODES and locale in ('iana', 'icao', 'faac'):
                    alt.kind = locale
                elif locale not in settings.locales and 'all' not in settings.locales:
                    self.logger.debug("Unknown alternative name type: {} -- skipping".format(locale))
                    continue

            alt.save()
            geo_info['object'].alt_names.add(alt)

            if not self.call_hook('alt_name_post', alt, item):
                continue

            self.logger.debug("Added alt name: %s, %s", locale, alt)

    def build_postal_code_regex_index(self):
        if hasattr(self, 'postal_code_regex_index') and self.postal_code_regex_index:
            return

        self.build_country_index()

        self.postal_code_regex_index = {}
        for code, country in tqdm(self.country_index.items(),
                                  disable=self.options.get('quiet'),
                                  total=len(self.country_index),
                                  desc="Building postal code regex index"):
            try:
                self.postal_code_regex_index[code] = re.compile(country.postal_code_regex)
            except Exception as e:
                self.logger.error("Couldn't compile postal code regex for {}: {}".format(country.code, e.args))
                self.postal_code_regex_index[code] = ''

    def import_postal_code(self):
        self.download('postal_code')
        data = self.get_data('postal_code')

        total = sum(1 for _ in data)

        data = self.get_data('postal_code')

        self.build_country_index()
        self.build_region_index()
        if VALIDATE_POSTAL_CODES:
            self.build_postal_code_regex_index()

        districts_to_delete = []

        query_statistics = [0 for i in range(8)]
        num_existing_postal_codes = PostalCode.objects.count()
        if num_existing_postal_codes == 0:
            self.logger.debug("Zero postal codes found - using only-create "
                              "postal code optimization")
        for item in tqdm(data, disable=self.options.get('quiet'), total=total, desc="Importing postal codes"):
            if not self.call_hook('postal_code_pre', item):
                continue

            country_code = item['countryCode']
            if country_code not in settings.postal_codes and 'ALL' not in settings.postal_codes:
                continue

            try:
                code = item['postalCode']
            except KeyError:
                self.logger.warning("Postal code has no code: {} -- skipping".format(item))
                continue

            # Find country
            try:
                country = self.country_index[country_code]
            except KeyError:
                self.logger.warning("Postal code '%s': Cannot find country: %s -- skipping", code, country_code)
                continue

            # Validate postal code against the country
            code = item['postalCode']
            if VALIDATE_POSTAL_CODES and self.postal_code_regex_index[country_code].match(code) is None:
                self.logger.warning("Postal code didn't validate: {} ({})".format(code, country_code))
                continue

            reg_name_q = Q(region_name__iexact=item['admin1Name'])
            subreg_name_q = Q(subregion_name__iexact=item['admin2Name'])
            dst_name_q = Q(district_name__iexact=item['admin3Name'])

            if hasattr(PostalCode, 'region'):
                reg_name_q |= Q(region__code=item['admin1Code'])

            if hasattr(PostalCode, 'subregion'):
                subreg_name_q |= Q(subregion__code=item['admin2Code'])

            if hasattr(PostalCode, 'district') and hasattr(District, 'code'):
                dst_name_q |= Q(district__code=item['admin3Code'])

            try:
                location = Point(float(item['longitude']),
                                 float(item['latitude']))
            except ValueError:
                location = None

            if len(item['placeName']) >= 200:
                self.logger.warning("Postal code name has more than 200 characters: {}".format(item))

            if num_existing_postal_codes > 0:
                postal_code_args = (
                    {
                        'args': (reg_name_q, subreg_name_q, dst_name_q),
                        'country': country,
                        'code': code,
                        'location': location,
                    }, {
                        'args': (reg_name_q, subreg_name_q, dst_name_q),
                        'country': country,
                        'code': code,
                    }, {
                        'args': (reg_name_q, subreg_name_q, dst_name_q),
                        'country': country,
                        'code': code,
                        'name__iexact': re.sub("'", '', item['placeName']),
                    }, {
                        'args': tuple(),
                        'country': country,
                        'region__code': item['admin1Code'],
                    }, {
                        'args': tuple(),
                        'country': country,
                        'code': code,
                        'name': item['placeName'],
                        'region__code': item['admin1Code'],
                        'subregion__code': item['admin2Code'],
                    }, {
                        'args': tuple(),
                        'country': country,
                        'code': code,
                        'name': item['placeName'],
                        'region__code': item['admin1Code'],
                        'subregion__code': item['admin2Code'],
                        'district__code': item['admin3Code'],
                    }, {
                        'args': tuple(),
                        'country': country,
                        'code': code,
                        'name': item['placeName'],
                        'region_name': item['admin1Name'],
                        'subregion_name': item['admin2Name'],
                    }, {
                        'args': tuple(),
                        'country': country,
                        'code': code,
                        'name': item['placeName'],
                        'region_name': item['admin1Name'],
                        'subregion_name': item['admin2Name'],
                        'district_name': item['admin3Name'],
                    }
                )

                # We do this so we don't have to deal with exceptions being thrown
                # in the middle of transactions
                for args_dict in postal_code_args:
                    num_pcs = PostalCode.objects.filter(
                        *args_dict['args'],
                        **{k: v for k, v in args_dict.items() if k != 'args'})\
                        .count()
                    if num_pcs == 1:
                        pc = PostalCode.objects.get(
                            *args_dict['args'],
                            **{k: v for k, v in args_dict.items() if k != 'args'})
                        break
                    elif num_pcs > 1:
                        pcs = PostalCode.objects.filter(
                            *args_dict['args'],
                            **{k: v for k, v in args_dict.items() if k != 'args'})
                        self.logger.debug("item: {}\nresults: {}".format(item, pcs))
                        # Raise a MultipleObjectsReturned exception
                        PostalCode.objects.get(
                            *args_dict['args'],
                            **{k: v for k, v in args_dict.items() if k != 'args'})
                else:
                    self.logger.debug("Creating postal code: {}".format(item))
                    pc = PostalCode(
                        country=country,
                        code=code,
                        name=item['placeName'],
                        region_name=item['admin1Name'],
                        subregion_name=item['admin2Name'],
                        district_name=item['admin3Name'])
            else:
                self.logger.debug("Creating postal code: {}".format(item))
                pc = PostalCode(
                    country=country,
                    code=code,
                    name=item['placeName'],
                    region_name=item['admin1Name'],
                    subregion_name=item['admin2Name'],
                    district_name=item['admin3Name'])

            if pc.region_name != '':
                try:
                    with transaction.atomic():
                        pc.region = Region.objects.get(
                            Q(name_std__iexact=pc.region_name) |
                            Q(name__iexact=pc.region_name),
                            country=pc.country)
                except Region.DoesNotExist:
                    pc.region = None
            else:
                pc.region = None

            if pc.subregion_name != '':
                try:
                    with transaction.atomic():
                        pc.subregion = Subregion.objects.get(
                            Q(region__name_std__iexact=pc.region_name) |
                            Q(region__name__iexact=pc.region_name),
                            Q(name_std__iexact=pc.subregion_name) |
                            Q(name__iexact=pc.subregion_name),
                            region__country=pc.country)
                except Subregion.DoesNotExist:
                    pc.subregion = None
            else:
                pc.subregion = None

            if pc.district_name != '':
                try:
                    with transaction.atomic():
                        pc.district = District.objects.get(
                            Q(city__region__name_std__iexact=pc.region_name) |
                            Q(city__region__name__iexact=pc.region_name),
                            Q(name_std__iexact=pc.district_name) |
                            Q(name__iexact=pc.district_name),
                            city__country=pc.country)
                except District.MultipleObjectsReturned as e:
                    self.logger.debug("item: {}\ndistricts: {}".format(
                        item,
                        District.objects.filter(
                            Q(city__region__name_std__iexact=pc.region_name) |
                            Q(city__region__name__iexact=pc.region_name),
                            Q(name_std__iexact=pc.district_name) |
                            Q(name__iexact=pc.district_name),
                            city__country=pc.country).values_list('id', flat=True)))
                    # If they're both part of the same city
                    if District.objects.filter(Q(city__region__name_std__iexact=pc.region_name) |
                                               Q(city__region__name__iexact=pc.region_name),
                                               Q(name_std__iexact=pc.district_name) |
                                               Q(name__iexact=pc.district_name),
                                               city__country=pc.country)\
                               .values_list('city').distinct().count() == 1:
                        # Use the one with the lower ID
                        pc.district = District.objects.filter(
                            Q(city__region__name_std__iexact=pc.region_name) |
                            Q(city__region__name__iexact=pc.region_name),
                            Q(name_std__iexact=pc.district_name) |
                            Q(name__iexact=pc.district_name),
                            city__country=pc.country).order_by('city__id').first()

                        districts_to_delete.append(District.objects.filter(
                            Q(city__region__name_std__iexact=pc.region_name) |
                            Q(city__region__name__iexact=pc.region_name),
                            Q(name_std__iexact=pc.district_name) |
                            Q(name__iexact=pc.district_name),
                            city__country=pc.country).order_by('city__id').last().id)
                    else:
                        raise e
                except District.DoesNotExist:
                    pc.district = None
            else:
                pc.district = None

            if pc.district is not None:
                pc.city = pc.district.city
            else:
                pc.city = None

            try:
                pc.location = Point(float(item['longitude']), float(item['latitude']))
            except Exception as e:
                self.logger.warning("Postal code %s (%s) - invalid location ('%s', '%s'): %s",
                                    pc.code, pc.country, item['longitude'],
                                    item['latitude'], str(e))
                pc.location = None

            pc.save()

            if not self.call_hook('postal_code_post', pc, item):
                continue

            self.logger.debug("Added postal code: %s, %s", pc.country, pc)

        if num_existing_postal_codes > 0 and max(query_statistics) > 0:
            width = int(math.log10(max(query_statistics)))

            stats_str = ""
            for i, count in enumerate(query_statistics):
                stats_str = "{{}}\n{{:>2}} [{{:>{}}}]: {{}}".format(width)\
                    .format(stats_str, i, count,
                            ''.join(['=' for i in range(count)]))

                self.logger.info("Postal code query statistics:\n{}".format(stats_str))

        if districts_to_delete:
            self.logger.debug('districts to delete:\n{}'.format(districts_to_delete))

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

    def flush_postal_code(self):
        self.logger.info("Flushing postal code data")
        PostalCode.objects.all().delete()

    def flush_alt_name(self):
        self.logger.info("Flushing alternate name data")
        for type_ in (Country, Region, Subregion, City, District, PostalCode):
            plural_type_name = type_.__name__ if type_.__name__[-1] != 'y' else '{}ies'.format(type_.__name__[:-1])
            for obj in tqdm(type_.objects.all(),
                            disable=self.options.get('quiet'),
                            total=type_.objects.count(),
                            desc="Flushing alternative names for {}".format(
                                plural_type_name)):
                obj.alt_names.all().delete()
