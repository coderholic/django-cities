from __future__ import division, unicode_literals

import collections
import itertools
import os
import datetime
import logging
from argparse import RawTextHelpFormatter
import sys
if sys.platform != 'win32':
    import resource

try:
    import cPickle as pickle
except ImportError:
    import pickle

from django.conf import settings
from django.db import transaction, connection
from django.db import reset_queries, IntegrityError
from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError

import progressbar

from ...exceptions import *
from ...signals import *
from ...settings import *
from ...geonames import Geonames
from ...loading import get_cities_models
from ...validators import timezone_validator

Country, Region, City = get_cities_models()


class MemoryUsageWidget(progressbar.widgets.WidgetBase):
    def __call__(self, progress, data):
        if sys.platform == 'win32':
            return '?? MB'
        rusage = resource.getrusage(resource.RUSAGE_SELF)
        if sys.platform == 'darwin':
            return '%s MB' % (rusage.ru_maxrss // 1048576)
        else:
            return '%s MB' % (rusage.ru_maxrss // 1024)


class Command(BaseCommand):
    help = """
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
    """.strip()

    logger = logging.getLogger('cities_light')

    def create_parser(self, *args, **kwargs):
        parser = super(Command, self).create_parser(*args, **kwargs)
        parser.formatter_class = RawTextHelpFormatter
        return parser

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
        parser.add_argument('--keep-slugs', action='store_true',
            default=False,
            help='Do not update slugs'
        ),
        parser.add_argument('--progress', action='store_true',
            default=False,
            help='Show progress bar'
        ),

    def progress_init(self):
        """Initialize progress bar."""
        if self.progress_enabled:
            self.progress_widgets = [
                'RAM used: ',
                MemoryUsageWidget(),
                ' ',
                progressbar.ETA(),
                ' Done: ',
                progressbar.Percentage(),
                progressbar.Bar(),
            ]

    def progress_start(self, max_value):
        """Start progress bar."""
        if self.progress_enabled:
            self.progress = progressbar.ProgressBar(
                max_value=max_value,
                widgets=self.progress_widgets
            ).start()

    def progress_update(self, value):
        """Update progress bar."""
        if self.progress_enabled:
            self.progress.update(value)

    def progress_finish(self):
        """Finalize progress bar."""
        if self.progress_enabled:
            self.progress.finish()

    def handle(self, *args, **options):
        # initialize lazy identity maps
        self._clear_identity_maps()

        if not os.path.exists(DATA_DIR):
            self.logger.info('Creating %s' % DATA_DIR)
            os.mkdir(DATA_DIR)

        install_file_path = os.path.join(DATA_DIR, 'install_datetime')
        translation_hack_path = os.path.join(DATA_DIR, 'translation_hack')

        self.noinsert = options.get('noinsert', False)
        self.keep_slugs = options.get('keep_slugs', False)
        self.progress_enabled = options.get('progress')

        self.progress_init()

        sources = list(itertools.chain(
            COUNTRY_SOURCES,
            REGION_SOURCES,
            CITY_SOURCES,
            TRANSLATION_SOURCES,
        ))

        for url in sources:
            if url in TRANSLATION_SOURCES:
                # free some memory
                self._clear_identity_maps()

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
                self.progress_start(geonames.num_lines())

                for items in geonames.parse():
                    if url in CITY_SOURCES:
                        self.city_import(items)
                    elif url in REGION_SOURCES:
                        self.region_import(items)
                    elif url in COUNTRY_SOURCES:
                        self.country_import(items)
                    elif url in TRANSLATION_SOURCES:
                        self.translation_parse(items)

                    # prevent memory leaks in DEBUG mode
                    # https://docs.djangoproject.com/en/1.9/faq/models/
                    # #how-can-i-see-the-raw-sql-queries-django-is-running
                    if settings.DEBUG:
                        reset_queries()

                    i += 1
                    self.progress_update(i)

                self.progress_finish()

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

    def _clear_identity_maps(self):
        """Clear identity maps and free some memory."""
        if getattr(self, '_country_codes', False):
            del self._country_codes
        if getattr(self, '_region_codes', False):
            del self._region_codes
        self._country_codes = {}
        self._region_codes = collections.defaultdict(dict)

    def _get_country_id(self, code2):
        """
        Simple lazy identity map for code2->country
        """
        if code2 not in self._country_codes:
            self._country_codes[code2] = Country.objects.get(code2=code2).pk

        return self._country_codes[code2]

    def _get_region_id(self, country_code2, region_id):
        """
        Simple lazy identity map for (country_code2, region_id)->region
        """
        country_id = self._get_country_id(country_code2)
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
            force_insert = False
            force_update = False
            country = Country.objects.get(geoname_id=items[ICountry.geonameid])
            force_update = True
        except Country.DoesNotExist:
            if self.noinsert:
                return
            country = Country(geoname_id=items[ICountry.geonameid])
            force_insert = True

        country.name = items[ICountry.name]
        country.code2 = items[ICountry.code2]
        country.code3 = items[ICountry.code3]
        country.continent = items[ICountry.continent]
        country.tld = items[ICountry.tld][1:]  # strip the leading dot
        # Strip + prefix for consistency. Note that some countries have several
        # prefixes ie. Puerto Rico
        country.phone = items[ICountry.phone].replace('+', '')
        # Clear name_ascii to always update it by set_name_ascii() signal
        country.name_ascii = ''

        if force_update and not self.keep_slugs:
            country.slug = None

        country_items_post_import.send(
            sender=self,
            instance=country,
            items=items
        )

        self.save(
            country,
            force_insert=force_insert,
            force_update=force_update
        )

    def region_import(self, items):
        try:
            region_items_pre_import.send(sender=self, items=items)
        except InvalidItems:
            return

        try:
            force_insert = False
            force_update = False
            region = Region.objects.get(geoname_id=items[IRegion.geonameid])
            force_update = True
        except Region.DoesNotExist:
            if self.noinsert:
                return
            region = Region(geoname_id=items[IRegion.geonameid])
            force_insert = True

        name = items[IRegion.name]
        if not items[IRegion.name]:
            name = items[IRegion.asciiName]

        code2, geoname_code = items[IRegion.code].split('.')
        country_id = self._get_country_id(code2)

        save = False
        if region.name != name:
            region.name = name
            save = True

        if region.country_id != country_id:
            region.country_id = country_id
            save = True

        if region.geoname_code != geoname_code:
            region.geoname_code = geoname_code
            save = True

        if region.name_ascii != items[IRegion.asciiName]:
            region.name_ascii = items[IRegion.asciiName]
            save = True

        if force_update and not self.keep_slugs:
            region.slug = None

        region_items_post_import.send(
            sender=self,
            instance=region,
            items=items
        )

        if save:
            self.save(
                region,
                force_insert=force_insert,
                force_update=force_update
            )

    def city_import(self, items):
        try:
            city_items_pre_import.send(sender=self, items=items)
        except InvalidItems:
            return

        try:
            force_insert = False
            force_update = False
            city = City.objects.get(geoname_id=items[ICity.geonameid])
            force_update = True
        except City.DoesNotExist:
            if self.noinsert:
                return
            city = City(geoname_id=items[ICity.geonameid])
            force_insert = True

        try:
            country_id = self._get_country_id(items[ICity.countryCode])
        except Country.DoesNotExist:
            if self.noinsert:
                return
            else:
                raise

        try:
            region_id = self._get_region_id(
                items[ICity.countryCode],
                items[ICity.admin1Code]
            )
        except Region.DoesNotExist:
            region_id = None

        save = False
        if city.country_id != country_id:
            city.country_id = country_id
            save = True

        if city.region_id != region_id:
            city.region_id = region_id
            save = True

        if city.name != items[ICity.name]:
            city.name = items[ICity.name]
            save = True

        if city.name_ascii != items[ICity.asciiName]:
            # useful for cities with chinese names
            city.name_ascii = items[ICity.asciiName]
            save = True

        if city.latitude != items[ICity.latitude]:
            city.latitude = items[ICity.latitude]
            save = True

        if city.longitude != items[ICity.longitude]:
            city.longitude = items[ICity.longitude]
            save = True

        if city.population != items[ICity.population]:
            city.population = items[ICity.population]
            save = True

        if city.feature_code != items[ICity.featureCode]:
            city.feature_code = items[ICity.featureCode]
            save = True

        if city.timezone != items[ICity.timezone]:
            try:
                timezone_validator(items[ICity.timezone])
                city.timezone = items[ICity.timezone]
            except ValidationError as e:
                city.timezone = None
                self.logger.warning(e.messages)
            save = True

        altnames = items[ICity.alternateNames]
        if not TRANSLATION_SOURCES and city.alternate_names != altnames:
            city.alternate_names = altnames
            save = True

        if force_update and not self.keep_slugs:
            city.slug = None

        city_items_post_import.send(
            sender=self,
            instance=city,
            items=items,
            save=save
        )

        if save:
            self.save(
                city,
                force_insert=force_insert,
                force_update=force_update
            )

    def translation_parse(self, items):
        if not hasattr(self, 'translation_data'):
            self.country_ids = set(Country.objects.values_list('geoname_id',
                flat=True))
            self.region_ids = set(Region.objects.values_list('geoname_id',
                flat=True))
            self.city_ids = set(City.objects.values_list('geoname_id',
                flat=True))

            self.translation_data = collections.OrderedDict((
                (Country, {}),
                (Region, {}),
                (City, {}),
            ))

        # https://code.djangoproject.com/ticket/21597#comment:29
        # https://github.com/yourlabs/django-cities-light/commit/e7f69af01760c450b4a72db84fda3d98d6731928
        if 'mysql' in settings.DATABASES['default']['ENGINE']:
            connection.close()

        try:
            translation_items_pre_import.send(sender=self, items=items)
        except InvalidItems:
            return

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
        self.progress_start(max)

        for model_class, model_class_data in data.items():
            for geoname_id, geoname_data in model_class_data.items():
                try:
                    model = model_class.objects.get(geoname_id=geoname_id)
                except model_class.DoesNotExist:
                    continue

                save = False
                alternate_names = set()
                for lang, names in geoname_data.items():
                    if lang == 'post':
                        # we might want to save the postal codes somewhere
                        # here's where it will all start ...
                        continue

                    for name in names:
                        if name == model.name:
                            continue

                        alternate_names.add(name)

                alternate_names = ';'.join(sorted(alternate_names))
                if model.alternate_names != alternate_names:
                    model.alternate_names = alternate_names
                    save = True

                if save:
                    model.save(force_update=True)

                i += 1
                self.progress_update(i)

        self.progress_finish()

    def save(self, model, force_insert=False, force_update=False):
        try:
            with transaction.atomic():
                self.logger.debug('Saving %s' % model.name)
                model.save(
                    force_insert=force_insert,
                    force_update=force_update
                )
        except IntegrityError as e:
            # Regarding %r see the https://code.djangoproject.com/ticket/20572
            # Also related to http://bugs.python.org/issue2517
            self.logger.warning('Saving %s failed: %r' % (model, e))
