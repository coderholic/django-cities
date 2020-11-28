"""Test for cities_light_fixtures management command."""
import bz2
import os
from unittest import mock

from django import test
from django.core.management import call_command
from django.core.management.base import CommandError

from dbdiff.fixture import Fixture
from cities_light.settings import DATA_DIR, FIXTURES_BASE_URL
from cities_light.management.commands.cities_light_fixtures import Command
from cities_light.downloader import Downloader
from cities_light.models import City
from .base import FixtureDir


class TestCitiesLigthFixtures(test.TransactionTestCase):
    """Tests for cities_light_fixtures management command."""

    def test_dump_fixtures(self):
        """
        Test dump_fixtures calls dump_fixture with Country,
        Region, Subregion and City table names.
        """
        fixtures_dir = os.path.join(DATA_DIR, 'fixtures')
        with mock.patch.object(Command, 'dump_fixture') as mock_func:
            cmd = Command()
            cmd.country_path = os.path.join(fixtures_dir, cmd.COUNTRY_FIXTURE)
            cmd.region_path = os.path.join(fixtures_dir, cmd.REGION_FIXTURE)
            cmd.subregion_path = os.path.join(fixtures_dir, cmd.SUBREGION_FIXTURE)
            cmd.city_path = os.path.join(fixtures_dir, cmd.CITY_FIXTURE)
            cmd.dump_fixtures()
            mock_func.assert_any_call('cities_light.Country', cmd.country_path)
            mock_func.assert_any_call('cities_light.Region', cmd.region_path)
            mock_func.assert_any_call('cities_light.SubRegion', cmd.subregion_path)
            mock_func.assert_any_call('cities_light.City', cmd.city_path)

    def test_dump_fixture(self):
        """
        Test dump_fixture calls dumpdata management command
        and tries to save it to file."""
        # Load test data
        destination = FixtureDir('import').get_file_path('angouleme.json')
        call_command('loaddata', destination)
        # Dump
        try:
            fixture_path = os.path.join(os.path.dirname(__file__), "fixtures", "test_dump_fixture.json")
            cmd = Command()
            cmd.dump_fixture('cities_light.City', fixture_path, True)
            with bz2.BZ2File(fixture_path, mode='r') as bzfile:
                data = bzfile.read()
            with open(fixture_path, mode='wb') as file:
                file.write(data)
            Fixture(fixture_path, models=[City]).assertNoDiff()
        finally:
            if os.path.exists(fixture_path):
                os.remove(fixture_path)

    def test_load_fixtures(self):
        """
        Test load_fixtures calls load_fixture with country,
        region, subregion and city path.
        """
        fixtures_dir = os.path.join(DATA_DIR, 'fixtures')
        with mock.patch.object(Command, 'load_fixture') as mock_func:
            cmd = Command()
            # paths
            cmd.country_path = os.path.join(fixtures_dir, cmd.COUNTRY_FIXTURE)
            cmd.region_path = os.path.join(fixtures_dir, cmd.REGION_FIXTURE)
            cmd.subregion_path = os.path.join(fixtures_dir, cmd.SUBREGION_FIXTURE)
            cmd.city_path = os.path.join(fixtures_dir, cmd.CITY_FIXTURE)
            # URLs
            cmd.country_url = FIXTURES_BASE_URL + cmd.COUNTRY_FIXTURE
            cmd.region_url = FIXTURES_BASE_URL + cmd.REGION_FIXTURE
            cmd.subregion_url = FIXTURES_BASE_URL + cmd.SUBREGION_FIXTURE
            cmd.city_url = FIXTURES_BASE_URL + cmd.CITY_FIXTURE

            cmd.load_fixtures(force_fetch=True)
            mock_func.assert_any_call(
                cmd.country_url, cmd.country_path, force=True)
            mock_func.assert_any_call(
                cmd.region_url, cmd.region_path, force=True)
            mock_func.assert_any_call(
                cmd.subregion_url, cmd.subregion_path, force=True)
            mock_func.assert_any_call(
                cmd.city_url, cmd.city_path, force=True)

    def test_load_fixture(self):
        """Test loaded fixture matches database content."""
        destination = FixtureDir('import').get_file_path('angouleme.json')
        with mock.patch.object(Downloader, 'download') as mock_func:
            cmd = Command()
            cmd.load_fixture(source='/abcdefg.json',
                             destination=destination,
                             force=True)
            Fixture(destination).assertNoDiff()
            mock_func.assert_called_with(source='/abcdefg.json',
                                         destination=destination,
                                         force=True)

    @mock.patch('cities_light.downloader.os.path.exists')
    def test_incorrect_subcommand(self, m_exists):
        """Test cities_light_fixtures fails on unsupported command."""
        m_exists.return_value = True
        with self.assertRaises(CommandError) as error:
            call_command('cities_light_fixtures', 'brrr')
        self.assertEqual(str(error.exception),
                         'Please specify either "load" or "dump" command')

    @mock.patch('cities_light.downloader.os.path.exists')
    def test_call_with_load_argument(self, m_exists):
        """Test 'cities_light_fixtures load' calls load method."""
        m_exists.return_value = True
        module = ('cities_light.management.commands.'
                  'cities_light_fixtures.Command.load_fixtures')
        with mock.patch(module) as mock_func:
            call_command('cities_light_fixtures', 'load')
            self.assertTrue(mock_func.called)

    @mock.patch('cities_light.downloader.os.path.exists')
    def test_call_with_dump_argument(self, m_exists):
        """Test 'cities_light_fixtures dump' calls dump method."""
        m_exists.return_value = True
        module = ('cities_light.management.commands.'
                  'cities_light_fixtures.Command.dump_fixtures')
        with mock.patch(module) as mock_func:
            call_command('cities_light_fixtures', 'dump')
            self.assertTrue(mock_func.called)

    @mock.patch('cities_light.downloader.os.path.exists')
    def test_call_with_base_url_and_fixtures_base_url_is_none(self, m_exists):
        """Test cities_light_fixtures --base-url option handling."""
        m_exists.return_value = True

        module = 'cities_light.management.commands.cities_light_fixtures'
        func = '{0}.{1}'.format(module, 'Command.load_fixtures')
        setting = '{0}.{1}'.format(module, 'FIXTURES_BASE_URL')

        with mock.patch(setting, None):
            # --base-url not specified
            with mock.patch(func) as _mock:
                exc = 'Please specify --base-url or settings'
                with self.assertRaisesRegex(CommandError, exc):
                    call_command('cities_light_fixtures', 'load')
            _mock.assert_not_called()

            # --base-url
            with mock.patch(func) as _mock:
                params = {'base_url': 'path/to/fixtures/for/load'}
                call_command('cities_light_fixtures', 'load', **params)
            self.assertTrue(_mock.called)
