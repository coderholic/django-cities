from __future__ import unicode_literals

import os
import mock

from django import test
from django.core.management import call_command

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
FIXTURE_DIR = os.path.abspath(os.path.join(BASE_DIR, 'tests', 'fixtures'))


def mock_source(setting, short_name):  # noqa
    return mock.patch(
        'cities_light.settings.%s_SOURCES' %
        setting.upper(), ['file://%s/%s.txt' % (FIXTURE_DIR, short_name)])


class TestUnicodeDecodeError(test.TransactionTestCase):
    """Test case which demonstrates UnicodeDecodeError."""

    @mock_source('city', 'kemerovo_city')
    @mock_source('region', 'kemerovo_region')
    @mock_source('country', 'kemerovo_country')
    def test_unicode_decode_error(self):
        """."""
        call_command('cities_light', force_import_all=True)
