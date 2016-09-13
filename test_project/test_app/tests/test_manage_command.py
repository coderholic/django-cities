# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.core.management import call_command

from cities.models import Region, City


class ManageCommandTestCase(TestCase):

    def test_manage_command(self):
        call_command('cities', force=True, **{
            'import': 'country,region,subregion,city',
        })
        self.assertEquals(Region.objects.filter(country__code='UA').count(), 27)
        self.assertEquals(City.objects.filter(region__country__code='UA').count(), 2)
