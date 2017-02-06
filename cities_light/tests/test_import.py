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
