"""Basic tests for contrib modules."""
import json

from django.test.utils import override_settings
from django.test.client import Client

from .base import TestImportBase, FixtureDir
from ..contrib.ajax_selects_lookups import (
    CountryLookup,
    RegionLookup,
    CityLookup
)


class TestRestFramework(TestImportBase):
    """Tests for django-rest-framework API endpoints."""

    longMessage = True

    json_headers = {
        'HTTP_ACCEPT': 'application/json'
    }

    def setUp(self):
        """Test init."""
        fixture_dir = FixtureDir('update')

        self.import_data(
            fixture_dir,
            'add_country',
            'add_region',
            'add_subregion',
            'add_city',
            'add_translations',
        )

        self.json_client = Client(**self.json_headers)

    def json_get(self, url):
        """Make GET request and assert that status is 200."""
        response = self.json_client.get(url)
        self.assertEqual(
            response.status_code, 200,
            msg='Status code should be 200'
        )
        return json.loads(response.content.decode('utf-8'))

    @override_settings(ROOT_URLCONF='cities_light.contrib.restframework3')
    def test_get_countries(self):
        """Test that full list of countries can be retrieved."""
        data = self.json_get('/countries/')
        self.assertEqual(len(data), 3, msg='Should retrieve 3 countries')
        names = [i['name_ascii'] for i in data]
        self.assertIn('Russia', names)
        self.assertIn('United Kingdom', names)
        self.assertIn('USSR', names)

    @override_settings(ROOT_URLCONF='cities_light.contrib.restframework3')
    def test_search_countries(self):
        """Test that search works for the list of countries."""
        data = self.json_get('/countries/?q=Gondor')
        self.assertEqual(len(data), 0, msg='Should find 0 countries')

        data = self.json_get('/countries/?q=SR')
        self.assertEqual(len(data), 1, msg='Should find 1 country')
        self.assertEqual(data[0]['name_ascii'], 'USSR')

    @override_settings(ROOT_URLCONF='cities_light.contrib.restframework3')
    def test_get_regions(self):
        """Test that full list of regions can be retrieved."""
        data = self.json_get('/regions/')
        self.assertEqual(len(data), 3, msg='Should retrieve 3 regions')
        self.assertEqual(data[0]['name_ascii'], 'Kemerovo')
        self.assertEqual(data[1]['name_ascii'], 'Kuzbass')
        self.assertEqual(data[2]['name_ascii'], 'Scotland')

    @override_settings(ROOT_URLCONF='cities_light.contrib.restframework3')
    def test_search_regions(self):
        """Test that search works for the list of regions."""
        data = self.json_get('/regions/?q=Anórien')
        self.assertEqual(len(data), 0, msg='Should find 0 regions')

        data = self.json_get('/regions/?q=uzB')
        self.assertEqual(len(data), 1, msg='Should find 1 region')
        self.assertEqual(data[0]['name_ascii'], 'Kuzbass')

    @override_settings(ROOT_URLCONF='cities_light.contrib.restframework3')
    def test_get_cities(self):
        """Test that full list of cities can be retrieved."""
        data = self.json_get('/cities/')
        self.assertEqual(len(data), 5, msg='Should retrieve 5 cities')
        self.assertEqual(data[0]['name_ascii'], 'Belovo')
        self.assertEqual(data[1]['name_ascii'], 'Kemerovo')
        self.assertEqual(data[2]['name_ascii'], 'Kiselevsk')
        self.assertEqual(data[3]['name_ascii'], 'Nedd')
        self.assertEqual(data[4]['name_ascii'], 'Novokuznetsk')

    @override_settings(ROOT_URLCONF='cities_light.contrib.restframework3')
    def test_search_cities(self):
        """Test that search works for the list of cities."""
        data = self.json_get('/cities/?q=Minas')
        self.assertEqual(len(data), 0, msg='Should find 0 cities')

        data = self.json_get('/cities/?q=ussr')
        self.assertEqual(len(data), 2, msg='Should find 2 cities')
        self.assertEqual(data[0]['name_ascii'], 'Belovo')
        self.assertEqual(data[1]['name_ascii'], 'Kiselevsk')


class TestAjaxSelectsLookups(TestImportBase):
    """Tests for ajax selects lookups."""

    longMessage = True

    def setUp(self):
        """Test init."""
        fixture_dir = FixtureDir('update')

        self.import_data(
            fixture_dir,
            'add_country',
            'add_region',
            'add_subregion',
            'add_city',
            'add_translations',
        )

    def test_country_lookup(self):
        """Test for CountryLookup.get_query method."""
        country_lookup = CountryLookup()
        lookup_query = country_lookup.get_query(q='Valinor', request=None)
        self.assertFalse(lookup_query.exists(), msg='Country should not exist')
        lookup_query = country_lookup.get_query(q='Russia', request=None)
        self.assertEqual(len(lookup_query), 1, msg='1 country should be found')
        self.assertEqual(lookup_query[0].name, 'Russia')
        lookup_query = country_lookup.get_query(q='sr', request=None)
        self.assertEqual(len(lookup_query), 1, msg='1 country should be found')
        self.assertEqual(lookup_query[0].name, 'USSR')
        lookup_query = country_lookup.get_query(q='us', request=None)
        self.assertEqual(
            len(lookup_query), 2,
            msg='2 countries should be found'
        )
        self.assertEqual(lookup_query[0].name, 'Russia')
        self.assertEqual(lookup_query[1].name, 'USSR')

    def test_region_lookup(self):
        """Test for RegionLookup.get_query method."""
        region_lookup = RegionLookup()
        lookup_query = region_lookup.get_query(q='Morthond Vale', request=None)
        self.assertFalse(lookup_query.exists(), msg='Region should not exist')
        lookup_query = region_lookup.get_query(q='Kuzbass', request=None)
        self.assertEqual(len(lookup_query), 1, msg='1 region should be found')
        self.assertEqual(lookup_query[0].name, 'Kuzbass')
        lookup_query = region_lookup.get_query(q='emer', request=None)
        self.assertEqual(len(lookup_query), 1, msg='1 region should be found')
        self.assertEqual(lookup_query[0].name, 'Kemerovo')
        lookup_query = region_lookup.get_query(q='K', request=None)
        self.assertEqual(
            len(lookup_query), 2,
            msg='2 regions should be found'
        )
        self.assertEqual(lookup_query[0].name, 'Kemerovo')
        self.assertEqual(lookup_query[1].name, 'Kuzbass')

    def test_city_lookup(self):
        """Test for CityLookup.get_query method."""
        city_lookup = CityLookup()
        lookup_query = city_lookup.get_query(q='Minas Morgul', request=None)
        self.assertFalse(lookup_query.exists(), msg='City should not exist')
        lookup_query = city_lookup.get_query(q='Novokuznetsk', request=None)
        self.assertEqual(len(lookup_query), 1, msg='1 city should be found')
        self.assertEqual(lookup_query[0].name, 'Novokuznetsk')
        lookup_query = city_lookup.get_query(q='ovo', request=None)
        self.assertEqual(len(lookup_query), 3, msg='3 cities should be found')
        self.assertEqual(lookup_query[0].name, 'Belovo')
        self.assertEqual(lookup_query[1].name, 'Kemerovo')
        self.assertEqual(lookup_query[2].name, 'Novokuznetsk')
