"""Management command to dump or load fixtures with geonames data."""

import os
import bz2
import logging
from argparse import RawTextHelpFormatter

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

from django.db import transaction
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from ...settings import DATA_DIR, FIXTURES_BASE_URL, CITIES_LIGHT_APP_NAME
from ...downloader import Downloader


class Command(BaseCommand):
    """Management command to dump or load fixtures with geonames data."""

    help = """
Dump or load fixtures with geonames data. Data dump is saved to
DATA_DIR/fixtures/, resulting in the following fixtures:

    cities_light_country.json.bz2
    cities_light_region.json.bz2
    cities_light_subregion.json.bz2
    cities_light_city.json.bz2

Loader by default uses the same DATA_DIR/fixtures/ folder (see
settings.CITIES_LIGHT_FIXTURES_BASE_URL), but you can customize its location
by specifying --base-url argument (do not forget the trailing slash):

    ./manage.py cities_light_fixtures load --base-url http://example.com/geo/

    or

    ./manage.py cities_light_fixtures load --base-url file:///tmp/folder/

It is possible to force fixture download by using the --force-fetch option:

    ./manage.py cities_light_fixtures load --force-fetch

It is possible to export using natural foreign keys by using the
--natural-foreign option (Take in consideration that this option will
going to take more time):

    ./manage.py cities_light_fixtures load --natural-foreign
    """.strip()

    logger = logging.getLogger('cities_light')

    COUNTRY_FIXTURE = 'cities_light_country.json.bz2'
    REGION_FIXTURE = 'cities_light_region.json.bz2'
    SUBREGION_FIXTURE = 'cities_light_subregion.json.bz2'
    CITY_FIXTURE = 'cities_light_city.json.bz2'

    def create_parser(self, *args, **kwargs):
        parser = super().create_parser(*args, **kwargs)
        parser.formatter_class = RawTextHelpFormatter
        return parser

    def add_arguments(self, parser):
        parser.add_argument(
            'subcommand',
            type=str,
            help='Subcommand (load/dump)'
        )
        parser.add_argument(
            '--natural-foreign',
            action='store_true',
            default=False,
            help='Export using natural foreign key'
        )
        parser.add_argument(
            '--force-fetch',
            action='store_true',
            default=False,
            help='Force fixture download'
        )
        parser.add_argument(
            '--base-url',
            action='store',
            metavar='BASE_URL',
            help='Base url to fetch from (default is '
                 'settings.CITIES_LIGHT_FIXTURES_BASE_URL)'
        )

    def handle(self, *args, **options):
        """Management command handler."""
        self.natural_foreign = options.get('natural_foreign')

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
        self.subregion_path = os.path.join(fixtures_dir,
                                           self.SUBREGION_FIXTURE)
        self.city_path = os.path.join(fixtures_dir,
                                      self.CITY_FIXTURE)

        subcommand = options.get('subcommand')

        if subcommand not in ('load', 'dump'):
            raise CommandError('Please specify either "load" '
                               'or "dump" command')

        if subcommand == 'load':
            base_url = options.get('base_url') or FIXTURES_BASE_URL
            if base_url is None:
                raise CommandError('Please specify --base-url or '
                                   'settings.CITIES_LIGHT_FIXTURES_BASE_URL')

            self.country_url = base_url + self.COUNTRY_FIXTURE
            self.region_url = base_url + self.REGION_FIXTURE
            self.subregion_url = base_url + self.SUBREGION_FIXTURE
            self.city_url = base_url + self.CITY_FIXTURE

            self.load_fixtures(**options)
        elif subcommand == 'dump':
            self.dump_fixtures()

    def dump_fixture(self, fixture, fixture_path,
                     natural_foreign: bool = False):
        """Dump single fixture."""
        self.logger.info('Dumping %s', fixture_path)

        out = StringIO()
        call_command('dumpdata',
                     fixture,
                     format="json",
                     natural_foreign=getattr(self, "natural_foreign",
                                             natural_foreign),
                     indent=1,
                     stdout=out)
        out.seek(0)
        with bz2.BZ2File(fixture_path, mode='w') as fixture_file:
            v = out.getvalue()
            fixture_file.write(v.encode())
        out.close()

    def dump_fixtures(self):
        """Dump Country/Region/City fixtures."""
        self.dump_fixture('{}.Country'.format(CITIES_LIGHT_APP_NAME),
                          self.country_path)
        self.dump_fixture('{}.Region'.format(CITIES_LIGHT_APP_NAME),
                          self.region_path)
        self.dump_fixture('{}.SubRegion'.format(CITIES_LIGHT_APP_NAME),
                          self.subregion_path)
        self.dump_fixture('{}.City'.format(CITIES_LIGHT_APP_NAME),
                          self.city_path)

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
        self.load_fixture(self.subregion_url, self.subregion_path, force=force)
        self.load_fixture(self.city_url, self.city_path, force=force)
