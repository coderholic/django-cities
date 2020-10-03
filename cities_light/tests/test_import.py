import glob
import os

from dbdiff.fixture import Fixture
from .base import TestImportBase, FixtureDir
from ..settings import DATA_DIR


class TestImport(TestImportBase):
    """Load test."""

    def test_single_city(self):
        """Load single city."""
        fixture_dir = FixtureDir('import')
        self.import_data(
            fixture_dir,
            'angouleme_country',
            'angouleme_region',
            'angouleme_subregion',
            'angouleme_city',
            'angouleme_translations'
        )
        Fixture(fixture_dir.get_file_path('angouleme.json')).assertNoDiff()

    def test_single_city_zip(self):
        """Load single city."""
        filelist = glob.glob(os.path.join(DATA_DIR, "angouleme_*.txt"))
        for f in filelist:
            os.remove(f)

        fixture_dir = FixtureDir('import_zip')
        self.import_data(
            fixture_dir,
            'angouleme_country',
            'angouleme_region',
            'angouleme_subregion',
            'angouleme_city',
            'angouleme_translations',
            file_type="zip"
        )
        Fixture(FixtureDir('import').get_file_path('angouleme.json')).assertNoDiff()

    def test_city_wrong_timezone(self):
        """Load single city with wrong timezone."""
        fixture_dir = FixtureDir('import')
        self.import_data(
            fixture_dir,
            'angouleme_country',
            'angouleme_region',
            'angouleme_subregion',
            'angouleme_city_wtz',
            'angouleme_translations'
        )
        Fixture(fixture_dir.get_file_path('angouleme_wtz.json')).assertNoDiff()

        from ..loading import get_cities_model
        city_model = get_cities_model('City')
        cities = city_model.objects.all()
        for city in cities:
            print(city.get_timezone_info().zone)

