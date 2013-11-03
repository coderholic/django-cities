from __future__ import unicode_literals

import os
import datetime
import time
import os.path
import logging
import optparse
import sys
if sys.platform != 'win32':
    import resource

try:
    import cPickle as pickle
except ImportError:
    import pickle

import progressbar

from django.db import transaction
from django.core.management.base import BaseCommand
from django.db import transaction, reset_queries, IntegrityError
from django.utils.encoding import force_text

from ...exceptions import *
from ...signals import *
from ...models import *
from ...settings import *
from ...geonames import Geonames


class MemoryUsageWidget(progressbar.Widget):
    def update(self, pbar):
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

    option_list = BaseCommand.option_list + (
        optparse.make_option('--force-import-all', action='store_true',
            default=False, help='Import even if files are up-to-date.'
        ),
        optparse.make_option('--force-all', action='store_true', default=False,
            help='Download and import if files are up-to-date.'
        ),
        optparse.make_option('--force-import', action='append', default=[],
            help='Import even if files matching files are up-to-date'
        ),
        optparse.make_option('--force', action='append', default=[],
            help='Download and import even if matching files are up-to-date'
        ),
        optparse.make_option('--noinsert', action='store_true',
            default=False,
            help='Update existing data only'
        ),
        optparse.make_option('--hack-translations', action='store_true',
            default=False,
            help='Set this if you intend to import translations a lot'
        ),
    )

    def _travis(self):
        if not os.environ.get('TRAVIS', False):
            return

        now = time.time()
        last_output = getattr(self, '_travis_last_output', None)

        if last_output is None or now - last_output >= 530:
            print('Do not kill me !')
            self._travis_last_output = now

    @transaction.commit_on_success
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

        for url in SOURCES:
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
                progress = progressbar.ProgressBar(maxval=geonames.num_lines(),
                    widgets=self.widgets).start()

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
            country = Country.objects.get(code2=items[0])
        except Country.DoesNotExist:
            if self.noinsert:
                return
            country = Country(code2=items[0])

        country.name = force_text(items[4])
        country.code3 = items[1]
        country.continent = items[8]
        country.tld = items[9][1:]  # strip the leading dot
        if items[16]:
            country.geoname_id = items[16]

        self.save(country)

    def region_import(self, items):
        try:
            region_items_pre_import.send(sender=self, items=items)
        except InvalidItems:
            return

        items = [force_text(x) for x in items]

        name = items[1]
        if not items[1]:
            name = items[2]

        code2, geoname_code = items[0].split('.')

        country_id = self._get_country_id(code2)

        if items[3]:
            kwargs = dict(geoname_id=items[3])
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
            region.name_ascii = items[2]

        region.geoname_id = items[3]
        self.save(region)

    def city_import(self, items):
        try:
            city_items_pre_import.send(sender=self, items=items)
        except InvalidItems:
            return

        try:
            country_id = self._get_country_id(items[8])
        except Country.DoesNotExist:
            if self.noinsert:
                return
            else:
                raise

        try:
            kwargs = dict(name=force_text(items[1]),
                country_id=self._get_country_id(items[8]))
        except Country.DoesNotExist:
            if self.noinsert:
                return
            else:
                raise

        try:
            city = City.objects.get(**kwargs)
        except City.DoesNotExist:
            try:
                city = City.objects.get(geoname_id=items[0])
                city.name = force_text(items[1])
                city.country_id = self._get_country_id(items[8])
            except City.DoesNotExist:
                if self.noinsert:
                    return

                city = City(**kwargs)

        save = False
        if not city.region_id:
            try:
                city.region_id = self._get_region_id(items[8], items[10])
            except Region.DoesNotExist:
                pass
            else:
                save = True

        if not city.name_ascii:
            # useful for cities with chinese names
            city.name_ascii = items[2]
            save = True

        if not city.latitude:
            city.latitude = items[4]
            save = True

        if not city.longitude:
            city.longitude = items[5]
            save = True

        if not city.population:
            city.population = items[14]
            save = True

        if not city.feature_code:
            city.feature_code = items[7]
            save = True

        if not TRANSLATION_SOURCES and not city.alternate_names:
            city.alternate_names = force_text(items[3])
            save = True

        if not city.geoname_id:
            # city may have been added manually
            city.geoname_id = items[0]
            save = True

        if save:
            self.save(city)

    def translation_parse(self, items):
        if not hasattr(self, 'translation_data'):
            self.country_ids = Country.objects.values_list('geoname_id',
                flat=True)
            self.region_ids = Region.objects.values_list('geoname_id',
                flat=True)
            self.city_ids = City.objects.values_list('geoname_id', flat=True)

            self.translation_data = {
                Country: {},
                Region: {},
                City: {},
            }

        if len(items) > 4:
            # avoid shortnames, colloquial, and historic
            return

        if items[2] not in TRANSLATION_LANGUAGES:
            return

        # arg optimisation code kills me !!!
        items[1] = int(items[1])

        if items[1] in self.country_ids:
            model_class = Country
        elif items[1] in self.region_ids:
            model_class = Region
        elif items[1] in self.city_ids:
            model_class = City
        else:
            return

        if items[1] not in self.translation_data[model_class]:
            self.translation_data[model_class][items[1]] = {}

        if items[2] not in self.translation_data[model_class][items[1]]:
            self.translation_data[model_class][items[1]][items[2]] = []

        self.translation_data[model_class][items[1]][items[2]].append(items[3])

    def translation_import(self):
        data = getattr(self, 'translation_data', None)

        if not data:
            return

        max = 0
        for model_class, model_class_data in data.items():
            max += len(model_class_data.keys())

        i = 0
        progress = progressbar.ProgressBar(maxval=max,
                                           widgets=self.widgets).start()
        for model_class, model_class_data in data.items():
            for geoname_id, geoname_data in model_class_data.items():
                try:
                    model = model_class.objects.get(geoname_id=geoname_id)
                except model_class.DoesNotExist:
                    continue
                save = False

                if not model.alternate_names:
                    alternate_names = []
                else:
                    alternate_names = model.alternate_names.split(',')

                for lang, names in geoname_data.items():
                    if lang == 'post':
                        # we might want to save the postal codes somewhere
                        # here's where it will all start ...
                        continue

                    for name in names:
                        name = force_text(name)
                        if name == model.name:
                            continue

                        if name not in alternate_names:
                            alternate_names.append(name)

                alternate_names = u','.join(alternate_names)
                if model.alternate_names != alternate_names:
                    model.alternate_names = alternate_names
                    save = True

                if save:
                    model.save()

                i += 1
                progress.update(i)

    def save(self, model):
        sid = transaction.savepoint()

        try:
            model.save()
        except IntegrityError as e:
            self.logger.warning('Saving %s failed: %s' % (model, e))
            transaction.savepoint_rollback(sid)
        else:
            transaction.savepoint_commit(sid)
