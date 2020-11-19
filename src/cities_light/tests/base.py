"""."""
import os
from unittest import mock

from django import test
from django.core import management
from django.conf import settings


class FixtureDir:
    """Helper class to construct fixture paths."""

    def __init__(self, rel_path='', base_dir=None):
        """Class constructor.

        params:
        rel_path - subdir relative to base dir, e.g. 'aaaa/bbbb/'
        base_dir - base fixture directory (settings.FIXTURE_DIR by default)
        """
        self.base_dir = base_dir or settings.FIXTURE_DIR
        self.rel_path = rel_path

    def get_file_path(self, file_name):
        """
        Get full fixture path.

        Concatenate base_dir, rel_path and file_name.
        """
        return os.path.abspath(
            os.path.join(self.base_dir, self.rel_path, file_name)
        )


class TestImportBase(test.TransactionTestCase):
    """Base class for import testcases.

    Inherit from this class and use separate
    fixture subdirectory for each test_*.py.
    """

    maxDiff = 100000
    reset_sequences = True

    def import_data(self, srcdir, countries, regions, subregions, cities, trans, file_type="txt", **options):
        """Helper method to import Geonames data.

        Patch *_SOURCES settings and call 'cities_light' command with
        --force-import-all option.

        params:
        srcdir - source directory represented by FixtureDir object.
        countries - values for COUNTRY_SOURCES
        regions - values for REGION_SOURCES
        subregions - values for SUBREGION_SOURCES
        cities - values for CITY_SOURCES
        trans - values for TRANSLATION_SOURCES
        **options - passed to call_command() as is
        """

        def _s2l(param):
            return param if isinstance(param, list) else [param]

        def _patch(setting, *values):
            setting_to_patch = (
                    'cities_light.management.commands.cities_light.%s_SOURCES' %
                    setting.upper()
            )

            return mock.patch(
                setting_to_patch,
                ['file://%s.%s' % (srcdir.get_file_path(v), file_type) for v in values]
            )

        m_country = _patch('country', *_s2l(countries))
        m_region = _patch('region', *_s2l(regions))
        m_subregion = _patch('subregion', *_s2l(subregions))
        m_city = _patch('city', *_s2l(cities))
        m_tr = _patch('translation', *_s2l(trans))
        with m_country, m_region, m_subregion, m_city, m_tr:
            management.call_command('cities_light', progress=True,
                                    force_import_all=True,
                                    **options)
