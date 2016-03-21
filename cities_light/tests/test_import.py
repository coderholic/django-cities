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


class ImportBase(test.TransactionTestCase):
    maxDiff = 100000
    reset_sequences = True

    def setUp(self):
        for m in [City, Region, Country]:
            m.objects.all().delete()

    def test_single_city(self):
        management.call_command('cities_light', force_import_all=True)
        Fixture('cities_light/tests/fixtures/angouleme.json').assertNoDiff()
