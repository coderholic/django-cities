from __future__ import unicode_literals

import pytest
import os
import itertools
import mock

from django import test
from django.core import management
from django.test.utils import override_settings

from dbdiff.fixture import Fixture
from cities_light.models import City, Region, Country
from cities_light.settings import DATA_DIR


def source(setting, short_name):
    return mock.patch(
        'cities_light.settings.%s_SOURCES' % setting.upper(),
        ['file://%s/%s.txt' % (DATA_DIR, short_name)]
    )


def translation_lang():
    return mock.patch(
        'cities_light.settings.TRANSLATION_LANGUAGES',
        ['fr', 'ru']
    )


class ImportBase(test.TransactionTestCase):
    maxDiff = 100000
    reset_sequences = True

    def setUp(self):
        for m in [City, Region, Country]:
            m.objects.all().delete()

    @translation_lang()
    @source('city', 'angouleme_city')
    @source('region', 'angouleme_region')
    @source('country', 'angouleme_country')
    @source('translation', 'angouleme_translations')
    def test_single_city(self):
        management.call_command('cities_light', force_import_all=True)
        Fixture('cities_light/tests/fixtures/angouleme.json').assertNoDiff()
