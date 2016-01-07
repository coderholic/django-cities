"""Management command to dump or load fixtures with geonames data."""

from __future__ import unicode_literals

import os
import bz2
import logging
import optparse

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

from django.db import transaction
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from ...settings import DATA_DIR, FIXTURES_BASE_URL
from ...downloader import Downloader


class Command(BaseCommand):

    """Management command to dump or load fixtures with geonames data."""

    args = '[--force-fetch] [--base-url BASE_URL] (load|dump)'
    help = '''
Dump or load fixtures with geonames data. Data dump is saved to
DATA_DIR/fixtures/, resulting in the following fixtures:

    cities_light_country.json.bz2
    cities_light_region.json.bz2
    cities_light_city.json.bz2

Loader by default uses the same DATA_DIR/fixtures/ folder (see
settings.CITIES_LIGHT_FIXTURES_BASE_URL), but you can customize its location
by specifying --base-url argument (do not forget the trailing slash):

    ./manage.py cities_light_fixtures load --base-url http://example.com/geo/

    or

    ./manage.py cities_light_fixtures load --base-url file:///tmp/folder/

It is possible to force fixture download by using the --force-fetch option:

    ./manage.py cities_light_fixtures load --force-fetch
    '''.strip()

    logger = logging.getLogger('cities_light')

    option_list = BaseCommand.option_list + (
        optparse.make_option('--force-fetch',
                             action='store_true',
                             default=False,
                             help='Force fetch'),
        optparse.make_option('--base-url',
                             action='store',
                             metavar='BASE_URL',
                             help='Base url to fetch from (default is '
                                  'settings.CITIES_LIGHT_FIXTURES_BASE_URL)'),
    )

    COUNTRY_FIXTURE = 'cities_light_country.json.bz2'
    REGION_FIXTURE = 'cities_light_region.json.bz2'
    CITY_FIXTURE = 'cities_light_city.json.bz2'

    def handle(self, *args, **options):
        """Management command handler."""
        if not os.path.exists(DATA_DIR):
            self.logger.info('Creating %s', DATA_DIR)
            os.mkdir(DATA_DIR)

        fixtures_dir = os.path.join(DATA_DIR, 'fixtures')
        if not os.path.exists(fixtures_dir):
            self.logger.info('Creating %s', fixtures_dir)
            os.mkdir(fixtures_dir)

        self.country_path = os.path.join(fixtures_dir,
                                         self.COUNTRY_FIXTURE)
        self.region_path = os.path.join(fixtures_dir,
                                        self.REGION_FIXTURE)
        self.city_path = os.path.join(fixtures_dir,
                                      self.CITY_FIXTURE)

        if len(args) != 1 or args[0] not in ('load', 'dump'):
            raise CommandError('Please specify either "load" '
                               'or "dump" command')

        if args[0] == 'load':
            base_url = options.get('base_url') or FIXTURES_BASE_URL
            if base_url is None:
                raise CommandError('Please specify --base-url or '
                                   'settings.CITIES_LIGHT_FIXTURES_BASE_URL')

            self.country_url = base_url + self.COUNTRY_FIXTURE
            self.region_url = base_url + self.REGION_FIXTURE
            self.city_url = base_url + self.CITY_FIXTURE

            self.load_fixtures(**options)
        elif args[0] == 'dump':
            self.dump_fixtures()

    def dump_fixture(self, fixture, fixture_path):
        """Dump single fixture."""
        self.logger.info('Dumping %s', fixture_path)
        out = StringIO()
        call_command('dumpdata',
                     fixture,
                     format="json",
                     indent=1,
                     stdout=out)
        out.seek(0)
        with bz2.BZ2File(fixture_path, mode='w') as fixture_file:
            v = out.getvalue()
            fixture_file.write(v.encode())
        out.close()

    def dump_fixtures(self):
        """Dump Country/Region/City fixtures."""
        self.dump_fixture('cities_light.Country', self.country_path)
        self.dump_fixture('cities_light.Region', self.region_path)
        self.dump_fixture('cities_light.City', self.city_path)

    def load_fixture(self, source, destination, force=False):
        """Download and import single fixture."""
        downloader = Downloader()
        self.logger.info('Loading %s', source)
        downloader.download(source=source,
                            destination=destination,
                            force=force)
        call_command('loaddata', destination)

    @transaction.atomic
    def load_fixtures(self, **options):
        """Download and import Country/Region/City fixtures."""
        force = options.get('force_fetch')
        self.load_fixture(self.country_url, self.country_path, force=force)
        self.load_fixture(self.region_url, self.region_path, force=force)
        self.load_fixture(self.city_url, self.city_path, force=force)
