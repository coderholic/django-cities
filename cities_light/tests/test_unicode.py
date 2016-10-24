# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import mock
import warnings

import six
import unidecode

from django import test
from django.core.management import call_command
from django.utils.encoding import force_text

from ..abstract_models import to_ascii


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
FIXTURE_DIR = os.path.abspath(os.path.join(BASE_DIR, 'tests', 'fixtures'))


def mock_source(setting, short_name):  # noqa
    return mock.patch(
        'cities_light.management.commands.cities_light.%s_SOURCES' %
        setting.upper(), ['file://%s/%s.txt' % (FIXTURE_DIR, short_name)])


class TestUnicode(test.TransactionTestCase):
    """Test case for unicode errors."""

    @mock_source('city', 'kemerovo_city')
    @mock_source('region', 'kemerovo_region')
    @mock_source('country', 'kemerovo_country')
    def test_exception_logging_unicode_error(self):
        """
        Test logging of duplicate row and UnicodeDecodeError.

        See issue https://github.com/yourlabs/django-cities-light/issues/61
        """
        call_command('cities_light', force_import_all=True)

    @mock_source('city', 'kemerovo_city')
    @mock_source('region', 'kemerovo_region')
    @mock_source('country', 'kemerovo_country')
    def test_unidecode_warning(self):
        """
        Unidecode should get unicode object and not byte string.

        unidecode/__init__.py:46: RuntimeWarning: Argument <type 'str'> is not an unicode object.
        Passing an encoded string will likely have unexpected results.

        This means to_ascii should return unicode string too.
        """
        # Reset warning registry to trigger the test if the warning was already issued
        # See http://bugs.python.org/issue21724
        registry = getattr(unidecode, '__warningregistry__', None)
        if registry:
            registry.clear()

        with warnings.catch_warnings(record=True) as warns:
            warnings.simplefilter('always')
            call_command('cities_light', force_import_all=True)
            for w in warns:
                warn = force_text(w.message)
                self.assertTrue("not an unicode object" not in warn, warn)

    def test_to_ascii(self):
        """Test to_ascii behavior."""
        self.assertEqual(to_ascii('République Françaisen'), 'Republique Francaisen')
        self.assertEqual(to_ascii('Кемерово'), 'Kemerovo')
        # Check that return value is unicode on python 2.7 or str on python 3
        self.assertTrue(isinstance(to_ascii('Кемерово'), six.text_type))
