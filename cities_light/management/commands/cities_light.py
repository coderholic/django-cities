from __future__ import division, unicode_literals

import collections
import itertools
import os
import datetime
import time
import logging
import optparse
import sys
if sys.platform != 'win32':
    import resource

try:
    import cPickle as pickle
except ImportError:
    import pickle

from django.db import transaction, connection
from django.db import reset_queries, IntegrityError
from django.core.management.base import BaseCommand
from django.utils.encoding import force_text

import progressbar

from ...exceptions import *
from ...signals import *
from ...settings import *
from ...geonames import Geonames
from ...loading import get_cities_models

Country, Region, City = get_cities_models()


class MemoryUsageWidget(progressbar.widgets.WidgetBase):
    def __call__(self, progress, data):
        if sys.platform != 'win32':
            return '%s kB' % resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return '?? kB'


class Command(BaseCommand):
    args = '''
[--force-all] [--force-import-all \\]
                              [--force-import countries.txt cities.txt ...] \\
                              [--force countries.txt cities.txt ...]
    '''.strip()
    help = '''
Download all files in CITIES_LIGHT_COUNTRY_SOURCES if they were updated or if
--force-all option was used.
Import country data if they were downloaded or if --force-import-all was used.

Same goes for CITIES_LIGHT_CITY_SOURCES.

It is possible to force the download of some files which have not been updated
on the server:

    manage.py --force cities15000 --force countryInfo

It is possible to force the import of files which weren't downloaded using the
--force-import option:

    manage.py --force-import cities15000 --force-import country
    '''.strip()

    logger = logging.getLogger('cities_light')

    def add_arguments(self, parser):
        parser.add_argument('--force-import-all', action='store_true',
            default=False, help='Import even if files are up-to-date.'
        ),
        parser.add_argument('--force-all', action='store_true', default=False,
            help='Download and import if files are up-to-date.'
        ),
        parser.add_argument('--force-import', action='append', default=[],
            help='Import even if files matching files are up-to-date'
        ),
        parser.add_argument('--force', action='append', default=[],
            help='Download and import even if matching files are up-to-date'
        ),
        parser.add_argument('--noinsert', action='store_true',
            default=False,
            help='Update existing data only'
        ),
        parser.add_argument('--hack-translations', action='store_true',
            default=False,
            help='Set this if you intend to import translations a lot'
        ),

    def _travis(self):
        if not os.environ.get('TRAVIS', False):
            return

        now = time.time()
        last_output = getattr(self, '_travis_last_output', None)

        if last_output is None or now - last_output >= 530:
            print('Do not kill me !')
            self._travis_last_output = now

    def handle(self, *args, **options):
        if not os.path.exists(DATA_DIR):
            self.logger.info('Creating %s' % DATA_DIR)
            os.mkdir(DATA_DIR)

        install_file_path = os.path.join(DATA_DIR, 'install_datetime')
        translation_hack_path = os.path.join(DATA_DIR, 'translation_hack')

        self.noinsert = options.get('noinsert', False)
        self.widgets = [
            'RAM used: ',
            MemoryUsageWidget(),
            ' ',
            progressbar.ETA(),
            ' Done: ',
            progressbar.Percentage(),
            progressbar.Bar(),
        ]
        sources = list(itertools.chain(
            COUNTRY_SOURCES,
            REGION_SOURCES,
            CITY_SOURCES,
            TRANSLATION_SOURCES,
        ))

        for url in sources:
            destination_file_name = url.split('/')[-1]

            force = options.get('force_all', False)
            if not force:
                for f in options['force']:
                    if f in destination_file_name or f in url:
                        force = True

            geonames = Geonames(url, force=force)
            downloaded = geonames.downloaded

            force_import = options.get('force_import_all', False)

            if not force_import:
                for f in options['force_import']:
                    if f in destination_file_name or f in url:
                        force_import = True

            if not os.path.exists(install_file_path):
                self.logger.info('Forced import of %s because data do not seem'
                        ' to have installed successfuly yet, note that this is'
                        ' equivalent to --force-import-all.' %
                        destination_file_name)
                force_import = True

            if downloaded or force_import:
                self.logger.info('Importing %s' % destination_file_name)

                if url in TRANSLATION_SOURCES:
                    if options.get('hack_translations', False):
                        if os.path.exists(translation_hack_path):
                            self.logger.debug(
                                'Using translation parsed data: %s' %
                                translation_hack_path)
                            continue

                i = 0
                progress = progressbar.ProgressBar(
                    max_value=geonames.num_lines(),
                    widgets=self.widgets
                ).start()

                for items in geonames.parse():
                    if url in CITY_SOURCES:
                        self.city_import(items)
                    elif url in REGION_SOURCES:
                        self.region_import(items)
                    elif url in COUNTRY_SOURCES:
                        self.country_import(items)
                    elif url in TRANSLATION_SOURCES:
                        # free some memory
                        if getattr(self, '_country_codes', False):
                            del self._country_codes
                        if getattr(self, '_region_codes', False):
                            del self._region_codes
                        self.translation_parse(items)

                    reset_queries()

                    i += 1
                    progress.update(i)

                    self._travis()

                progress.finish()

                if url in TRANSLATION_SOURCES and options.get(
                        'hack_translations', False):
                    with open(translation_hack_path, 'w+') as f:
                        pickle.dump(self.translation_data, f)

        if options.get('hack_translations', False):
            with open(translation_hack_path, 'r') as f:
                self.translation_data = pickle.load(f)

        self.logger.info('Importing parsed translation in the database')
        self.translation_import()

        with open(install_file_path, 'wb+') as f:
            pickle.dump(datetime.datetime.now(), f)

    def _get_country_id(self, code2):
        '''
        Simple lazy identity map for code2->country
        '''
        if not hasattr(self, '_country_codes'):
            self._country_codes = {}

        if code2 not in self._country_codes.keys():
            self._country_codes[code2] = Country.objects.get(code2=code2).pk

        return self._country_codes[code2]

    def _get_region_id(self, country_code2, region_id):
        '''
        Simple lazy identity map for (country_code2, region_id)->region
        '''
        if not hasattr(self, '_region_codes'):
            self._region_codes = {}

        country_id = self._get_country_id(country_code2)
        if country_id not in self._region_codes:
            self._region_codes[country_id] = {}

        if region_id not in self._region_codes[country_id]:
            self._region_codes[country_id][region_id] = Region.objects.get(
                country_id=country_id, geoname_code=region_id).pk

        return self._region_codes[country_id][region_id]

    def country_import(self, items):
        try:
            country_items_pre_import.send(sender=self, items=items)
        except InvalidItems:
            return
        try:
            country = Country.objects.get(code2=items[ICountry.code])
        except Country.DoesNotExist:
            if self.noinsert:
                return
            country = Country(code2=items[ICountry.code])

        country.name = force_text(items[ICountry.name])
        # Strip + prefix for consistency. Note that some countries have several
        # prefixes ie. Puerto Rico
        country.phone = items[ICountry.phone].replace('+', '')
        country.code3 = items[ICountry.code3]
        country.continent = items[ICountry.continent]
        country.tld = items[ICountry.tld][1:]  # strip the leading dot
        if items[ICountry.geonameid]:
            country.geoname_id = items[ICountry.geonameid]

        country_items_post_import.send(sender=self, instance=country,
            items=items)

        self.save(country)

    def region_import(self, items):
        try:
            region_items_pre_import.send(sender=self, items=items)
        except InvalidItems:
            return

        items = [force_text(x) for x in items]

        name = items[IRegion.name]
        if not items[IRegion.name]:
            name = items[IRegion.asciiName]

        code2, geoname_code = items[IRegion.code].split('.')

        country_id = self._get_country_id(code2)

        if items[IRegion.geonameid]:
            kwargs = dict(geoname_id=items[IRegion.geonameid])
        else:
            kwargs = dict(name=name, country_id=country_id)

        try:
            region = Region.objects.get(**kwargs)
        except Region.DoesNotExist:
            if self.noinsert:
                return
            region = Region(**kwargs)

        if not region.name:
            region.name = name

        if not region.country_id:
            region.country_id = country_id

        if not region.geoname_code:
            region.geoname_code = geoname_code

        if not region.name_ascii:
            region.name_ascii = items[IRegion.asciiName]

        region.geoname_id = items[IRegion.geonameid]

        region_items_post_import.send(sender=self, instance=region,
            items=items)

        self.save(region)

    def city_import(self, items):
        try:
            city_items_pre_import.send(sender=self, items=items)
        except InvalidItems:
            return

        try:
            country_id = self._get_country_id(items[ICity.countryCode])
        except Country.DoesNotExist:
            if self.noinsert:
                return
            else:
                raise

        try:
            kwargs = dict(name=force_text(items[ICity.name]),
                country_id=self._get_country_id(items[ICity.countryCode]))
        except Country.DoesNotExist:
            if self.noinsert:
                return
            else:
                raise

        try:
            kwargs['region_id'] = self._get_region_id(items[ICity.countryCode],
                items[ICity.admin1Code])
        except Region.DoesNotExist:
            pass

        try:
            try:
                city = City.objects.get(**kwargs)
            except City.MultipleObjectsReturned:
                if 'region_id' not in kwargs:
                    self.logger.warn(
                        'Skipping because of invalid region: %s' % items)
                    return
                else:
                    raise

        except City.DoesNotExist:
            try:
                city = City.objects.get(geoname_id=items[ICity.geonameid])
                city.name = force_text(items[ICity.name])
                city.country_id = self._get_country_id(
                    items[ICity.countryCode])
            except City.DoesNotExist:
                if self.noinsert:
                    return

                city = City(**kwargs)

        save = False
        if not city.region_id and 'region_id' in kwargs:
            city.region_id = kwargs['region_id']
            save = True

        if not city.name_ascii:
            # useful for cities with chinese names
            city.name_ascii = items[ICity.asciiName]
            save = True

        if not city.latitude:
            city.latitude = items[ICity.latitude]
            save = True

        if not city.longitude:
            city.longitude = items[ICity.longitude]
            save = True

        if not city.population:
            city.population = items[ICity.population]
            save = True

        if not city.feature_code:
            city.feature_code = items[ICity.featureCode]
            save = True

        if not TRANSLATION_SOURCES and not city.alternate_names:
            city.alternate_names = force_text(items[ICity.alternateNames])
            save = True

        if not city.geoname_id:
            # city may have been added manually
            city.geoname_id = items[ICity.geonameid]
            save = True

        city_items_post_import.send(sender=self, instance=city,
            items=items, save=save)

        if save:
            self.save(city)

    def translation_parse(self, items):
        if not hasattr(self, 'translation_data'):
            self.country_ids = list(Country.objects.values_list('geoname_id',
                flat=True))
            self.region_ids = list(Region.objects.values_list('geoname_id',
                flat=True))
            self.city_ids = list(City.objects.values_list('geoname_id',
                flat=True))

            self.translation_data = collections.OrderedDict((
                (Country, {}),
                (Region, {}),
                (City, {}),
            ))

        connection.close()

        if len(items) > 5:
            # avoid shortnames, colloquial, and historic
            return

        item_lang = items[IAlternate.language]

        if item_lang not in TRANSLATION_LANGUAGES:
            return

        item_geoid = items[IAlternate.geonameid]
        item_name = items[IAlternate.name]

        # arg optimisation code kills me !!!
        item_geoid = int(item_geoid)

        if item_geoid in self.country_ids:
            model_class = Country
        elif item_geoid in self.region_ids:
            model_class = Region
        elif item_geoid in self.city_ids:
            model_class = City
        else:
            return

        if item_geoid not in self.translation_data[model_class]:
            self.translation_data[model_class][item_geoid] = {}

        if item_lang not in self.translation_data[model_class][item_geoid]:
            self.translation_data[model_class][item_geoid][item_lang] = []

        self.translation_data[model_class][item_geoid][item_lang].append(
            item_name)

    def translation_import(self):
        data = getattr(self, 'translation_data', None)

        if not data:
            return

        max = 0
        for model_class, model_class_data in data.items():
            max += len(model_class_data.keys())

        i = 0
        progress = progressbar.ProgressBar(
            max_value=max,
            widgets=self.widgets
        ).start()

        for model_class, model_class_data in data.items():
            for geoname_id, geoname_data in model_class_data.items():
                try:
                    model = model_class.objects.get(geoname_id=geoname_id)
                except model_class.DoesNotExist:
                    continue
                save = False

                if not model.alternate_names:
                    alternate_names = set()
                else:
                    alternate_names = set(sorted(
                        model.alternate_names.split(',')))

                for lang, names in geoname_data.items():
                    if lang == 'post':
                        # we might want to save the postal codes somewhere
                        # here's where it will all start ...
                        continue

                    for name in names:
                        name = force_text(name)

                        if name == model.name:
                            continue

                        alternate_names.add(name)

                alternate_names = u','.join(sorted(alternate_names))
                if model.alternate_names != alternate_names:
                    model.alternate_names = alternate_names
                    save = True

                if save:
                    model.save()

                i += 1
                progress.update(i)

        progress.finish()

    def save(self, model):
        try:
            with transaction.atomic():
                self.logger.debug('Saving %s' % model.name)
                model.save()
        except IntegrityError as e:
            self.logger.warning('Saving %s failed: %s' % (model, e))
