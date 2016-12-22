# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase, override_settings
from django.core.management import call_command

from cities.models import Country, Region, Subregion, City, PostalCode
from cities.util import unicode_func


@override_settings(CITIES_IGNORE_EMPTY_REGIONS=True)
class IgnoreEmptyRegionManageCommandTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        # Run the import command only once
        super(IgnoreEmptyRegionManageCommandTestCase, cls).setUpClass()
        call_command('cities', force=True, **{
            'import': 'country,region,subregion,city',
        })
        cls.counts = {
            'countries': Country.objects.count(),
            'regions': Region.objects.count(),
            'subregions': Subregion.objects.count(),
            'cities': City.objects.count(),
            'postal_codes': PostalCode.objects.count(),
        }

    def test_no_invalid_slugs(self):
        self.assertEqual(Country.objects.filter(slug__startswith='invalid').count(), 0)
        self.assertEqual(Region.objects.filter(slug__startswith='invalid').count(), 0)
        self.assertEqual(Subregion.objects.filter(slug__startswith='invalid').count(), 0)
        self.assertEqual(City.objects.filter(slug__startswith='invalid').count(), 0)
        self.assertEqual(PostalCode.objects.filter(slug__startswith='invalid').count(), 0)

    def test_imported_all_countries(self):
        self.assertEqual(Country.objects.all().count(), 250)

    def test_imported_ad_regions(self):
        self.assertEqual(Region.objects.filter(country__code='AD').count(), 7)

    def test_imported_ua_regions(self):
        self.assertEqual(Region.objects.filter(country__code='UA').count(), 27)

    def test_imported_ua_cities(self):
        self.assertEqual(City.objects.filter(region__country__code='UA').count(), 50)


class ManageCommandTestCase(IgnoreEmptyRegionManageCommandTestCase):
    @classmethod
    def setUpClass(cls):
        # Run the import command only once
        super(IgnoreEmptyRegionManageCommandTestCase, cls).setUpClass()
        call_command('cities', force=True, **{
            'import': 'country,region,subregion,city,postal_code',
        })
        cls.counts = {
            'countries': Country.objects.count(),
            'regions': Region.objects.count(),
            'subregions': Subregion.objects.count(),
            'cities': City.objects.count(),
            'postal_codes': PostalCode.objects.count(),
        }

    def test_postal_code_slugs(self):
        self.assertEqual(PostalCode.objects.get(country__code='RU', code='102104').code, '102104')
        self.assertTrue(len(PostalCode.objects.get(country__code='RU', code='102104').slug) <= 255)
        self.assertEqual(PostalCode.objects.get(country__code='RU', code='102104').slug, unicode_func('1-102104'))

    def test_idempotence(self):
        call_command('cities', force=True, **{
            'import': 'country,region,subregion,city,postal_code',
        })
        self.assertEqual(Country.objects.count(), self.counts['countries'])
        self.assertEqual(Region.objects.count(), self.counts['regions'])
        self.assertEqual(Subregion.objects.count(), self.counts['subregions'])
        self.assertEqual(City.objects.count(), self.counts['cities'])
        self.assertEqual(PostalCode.objects.count(), self.counts['postal_codes'])
