# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

from django.test import TestCase, override_settings
from django.core.management import call_command

from cities.models import (Country, Region, Subregion, City, PostalCode,
                           AlternativeName)


class NoInvalidSlugsTestCaseMixin(object):
    def test_no_invalid_slugs(self):
        self.assertEqual(Country.objects.filter(slug__startswith='invalid').count(), 0)
        self.assertEqual(Region.objects.filter(slug__startswith='invalid').count(), 0)
        self.assertEqual(Subregion.objects.filter(slug__startswith='invalid').count(), 0)
        self.assertEqual(City.objects.filter(slug__startswith='invalid').count(), 0)
        self.assertEqual(PostalCode.objects.filter(slug__startswith='invalid').count(), 0)


class CountriesTestCaseMixin(object):
    def test_num_countries(self):
        self.assertEqual(Country.objects.all().count(), self.num_countries)


class RegionsTestCaseMixin(object):
    def test_num_regions(self):
        self.assertEqual(Region.objects.count(), self.num_regions)

    def test_num_ad_regions(self):
        self.assertEqual(
            Region.objects.filter(country__code='AD').count(),
            self.num_ad_regions)

    def test_num_ua_regions(self):
        self.assertEqual(
            Region.objects.filter(country__code='UA').count(),
            self.num_ua_regions)


class SubregionsTestCaseMixin(object):
    def test_num_subregions(self):
        self.assertEqual(Subregion.objects.count(), self.num_subregions)


class CitiesTestCaseMixin(object):
    def test_num_cities(self):
        self.assertEqual(City.objects.count(), self.num_cities)

    def test_num_ua_cities(self):
        self.assertEqual(
            City.objects.filter(region__country__code='UA').count(),
            self.num_ua_cities)


class AlternativeNameTestCaseMixin(object):
    def test_num_alternative_names(self):
        self.assertEqual(AlternativeName.objects.count(), self.num_alt_names)

    def test_num_not_und_alternative_names(self):
        self.assertEqual(
            AlternativeName.objects.exclude(language_code='und').count(),
            self.num_not_und_alt_names)


class PostalCodeTestCaseMixin(object):
    def test_num_postal_codes(self):
        self.assertEqual(PostalCode.objects.count(), self.num_postal_codes)

    def test_postal_code_slugs(self):
        pc = PostalCode.objects.get(country__code='RU', code='102104')
        self.assertEqual(pc.code, '102104')
        self.assertTrue(len(pc.slug) <= 255)

        slug_rgx = re.compile(r'\d+-102104', re.UNICODE)

        slug = PostalCode.objects.get(country__code='RU', code='102104').slug

        # The unittest module in Python 2 does not have an assertRegex
        if hasattr(self, 'assertRegex'):
            self.assertRegex(slug, slug_rgx)
        else:
            m = slug_rgx.match(slug)

            self.assertIsNotNone(m)
            self.assertEqual(m.group(0)[-7:], '-102104')


@override_settings(CITIES_IGNORE_EMPTY_REGIONS=True)
class IgnoreEmptyRegionManageCommandTestCase(
        NoInvalidSlugsTestCaseMixin, CountriesTestCaseMixin,
        RegionsTestCaseMixin, SubregionsTestCaseMixin, CitiesTestCaseMixin,
        TestCase):
    num_countries = 250
    num_regions = 170
    num_ad_regions = 7
    num_ua_regions = 27
    num_subregions = 4926
    num_cities = 114
    num_ua_cities = 50

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


class ManageCommandTestCase(
        NoInvalidSlugsTestCaseMixin, CountriesTestCaseMixin,
        RegionsTestCaseMixin, SubregionsTestCaseMixin, CitiesTestCaseMixin,
        AlternativeNameTestCaseMixin, PostalCodeTestCaseMixin, TestCase):
    num_countries = 250
    num_regions = 170
    num_ad_regions = 7
    num_ua_regions = 27
    num_subregions = 4926
    num_cities = 114
    num_ua_cities = 50
    num_alt_names = 2945
    num_not_und_alt_names = 579
    num_postal_codes = 13

    @classmethod
    def setUpClass(cls):
        # Run the import command only once
        super(ManageCommandTestCase, cls).setUpClass()
        call_command('cities', force=True, **{
            'import': 'country,region,subregion,city,alt_name,postal_code',
        })
        cls.counts = {
            'countries': Country.objects.count(),
            'regions': Region.objects.count(),
            'subregions': Subregion.objects.count(),
            'cities': City.objects.count(),
            'alt_names': AlternativeName.objects.count(),
            'postal_codes': PostalCode.objects.count(),
        }

    def test_only_en_and_und_alternative_names(self):
        self.assertEqual(
            AlternativeName.objects.count(),
            AlternativeName.objects.filter(language_code__in=['en', 'und']).count())

    def test_idempotence(self):
        call_command('cities', force=True, **{
            'import': 'country,region,subregion,city,alt_name,postal_code',
        })
        self.assertEqual(Country.objects.count(), self.counts['countries'])
        self.assertEqual(Region.objects.count(), self.counts['regions'])
        self.assertEqual(Subregion.objects.count(), self.counts['subregions'])
        self.assertEqual(City.objects.count(), self.counts['cities'])
        self.assertEqual(AlternativeName.objects.count(), self.counts['alt_names'])
        self.assertEqual(PostalCode.objects.count(), self.counts['postal_codes'])


@override_settings(CITIES_LOCALES=['all'])
class AllLocalesManageCommandTestCase(
        NoInvalidSlugsTestCaseMixin, CountriesTestCaseMixin,
        RegionsTestCaseMixin, SubregionsTestCaseMixin, CitiesTestCaseMixin,
        AlternativeNameTestCaseMixin, TestCase):
    num_countries = 250
    num_regions = 170
    num_ad_regions = 7
    num_ua_regions = 27
    num_subregions = 4926
    num_cities = 114
    num_ua_cities = 50
    num_alt_names = 7760
    num_not_und_alt_names = 5394

    @classmethod
    def setUpClass(cls):
        # Run the import command only once
        super(AllLocalesManageCommandTestCase, cls).setUpClass()
        call_command('cities', force=True, **{
            'import': 'country,region,subregion,city,alt_name',
        })
        cls.counts = {
            'countries': Country.objects.count(),
            'regions': Region.objects.count(),
            'subregions': Subregion.objects.count(),
            'cities': City.objects.count(),
            'alt_names': AlternativeName.objects.count(),
        }
