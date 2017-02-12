"""Tests for update records."""
from __future__ import unicode_literals

from dbdiff.fixture import Fixture
from .base import TestImportBase, FixtureDir


class TestUpdate(TestImportBase):
    """Tests update procedure."""

    def test_update_fields(self):
        """Test all fields are updated."""
        fixture_dir = FixtureDir('update')

        self.import_data(
            fixture_dir,
            'initial_country',
            'initial_region',
            'initial_city',
            'initial_translations'
        )

        self.import_data(
            fixture_dir,
            'update_country',
            'update_region',
            'update_city',
            'update_translations',
        )

        Fixture(
            fixture_dir.get_file_path('update_fields.json')
        ).assertNoDiff()

    def test_change_country(self):
        """Test change country for region/city."""
        fixture_dir = FixtureDir('update')

        self.import_data(
            fixture_dir,
            'initial_country',
            'initial_region',
            'initial_city',
            'initial_translations'
        )

        self.import_data(
            fixture_dir,
            'change_country',
            'update_region',
            'update_city',
            'update_translations',
        )

        Fixture(
            fixture_dir.get_file_path('change_country.json')
        ).assertNoDiff()

    def test_change_region_and_country(self):
        """Test change region and country."""
        fixture_dir = FixtureDir('update')

        self.import_data(
            fixture_dir,
            'initial_country',
            'initial_region',
            'initial_city',
            'initial_translations'
        )

        self.import_data(
            fixture_dir,
            'change_country',
            'change_region',
            'update_city',
            'update_translations',
        )

        Fixture(
            fixture_dir.get_file_path('change_region_and_country.json')
        ).assertNoDiff()

    def test_keep_slugs(self):
        """Test --keep-slugs option."""
        fixture_dir = FixtureDir('update')

        self.import_data(
            fixture_dir,
            'initial_country',
            'initial_region',
            'initial_city',
            'initial_translations'
        )

        self.import_data(
            fixture_dir,
            'update_country',
            'update_region',
            'update_city',
            'update_translations',
            keep_slugs=True
        )

        Fixture(
            fixture_dir.get_file_path('keep_slugs.json'),
        ).assertNoDiff()
