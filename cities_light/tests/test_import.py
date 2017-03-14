from __future__ import unicode_literals

from dbdiff.fixture import Fixture
from .base import TestImportBase, FixtureDir


class TestImport(TestImportBase):
    """Load test."""

    def test_single_city(self):
        """Load single city."""
        fixture_dir = FixtureDir('import')
        self.import_data(
            fixture_dir,
            'angouleme_country',
            'angouleme_region',
            'angouleme_city',
            'angouleme_translations'
        )
        Fixture(fixture_dir.get_file_path('angouleme.json')).assertNoDiff()

    def test_city_wrong_timezone(self):
        """Load single city with wrong timezone."""
        fixture_dir = FixtureDir('import')
        self.import_data(
            fixture_dir,
            'angouleme_country',
            'angouleme_region',
            'angouleme_city_wtz',
            'angouleme_translations'
        )
        Fixture(fixture_dir.get_file_path('angouleme_wtz.json')).assertNoDiff()

        from ..loading import get_cities_model
        city_model = get_cities_model('City')
        cities = city_model.objects.all()
        for city in cities:
            print(city.get_timezone_info().zone)

