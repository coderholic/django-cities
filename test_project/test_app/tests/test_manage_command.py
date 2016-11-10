# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import os

from django.test import TestCase
from django.core.management import call_command

from cities.models import Country, Region, City, PostalCode


# Only log errors during Travis tests
logger = logging.getLogger(os.environ.get('TRAVIS_LOGGER_NAME', 'cities'))


class ManageCommandTestCase(TestCase):

    def test_manage_command(self):
        call_command('cities', force=True, **{
            'import': 'country,region,subregion,city,postal_code',
        })
        self.assertEquals(Country.objects.all().count(), 250)
        self.assertEquals(Region.objects.filter(country__code='AD').count(), 7)
        self.assertEquals(Region.objects.filter(country__code='UA').count(), 27)
        self.assertEquals(City.objects.filter(region__country__code='UA').count(), 2)
        self.assertEquals(PostalCode.objects.get(country__code='RU', code='102104').values('code'), '102104')
