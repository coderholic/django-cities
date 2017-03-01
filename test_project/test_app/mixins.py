# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

from cities.models import (Continent, Country, Region, Subregion, City,
                           District, PostalCode, AlternativeName)
from cities.util import add_continents


class NoInvalidSlugsMixin(object):
    def test_no_invalid_slugs(self):
        self.assertEqual(Country.objects.filter(slug__startswith='invalid').count(), 0)
        self.assertEqual(Region.objects.filter(slug__startswith='invalid').count(), 0)
        self.assertEqual(Subregion.objects.filter(slug__startswith='invalid').count(), 0)
        self.assertEqual(City.objects.filter(slug__startswith='invalid').count(), 0)
        self.assertEqual(PostalCode.objects.filter(slug__startswith='invalid').count(), 0)


class ContinentsMixin(object):
    num_continents = 7

    def setUp(self):
        super(ContinentsMixin, self).setUp()
        Continent.objects.all().delete()
        add_continents(Continent)

    def test_num_continents(self):
        self.assertEqual(Continent.objects.count(), self.num_continents)


class CountriesMixin(object):
    def test_num_countries(self):
        self.assertEqual(Country.objects.all().count(), self.num_countries)


class RegionsMixin(object):
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


class SubregionsMixin(object):
    def test_num_subregions(self):
        self.assertEqual(Subregion.objects.count(), self.num_subregions)


class CitiesMixin(object):
    def test_num_cities(self):
        self.assertEqual(City.objects.count(), self.num_cities)

    def test_num_ua_cities(self):
        self.assertEqual(
            City.objects.filter(region__country__code='UA').count(),
            self.num_ua_cities)


class DistrictsMixin(object):
    def test_num_districts(self):
        self.assertEqual(District.objects.count(), self.num_districts)


class AlternativeNamesMixin(object):
    def test_num_alternative_names(self):
        self.assertEqual(AlternativeName.objects.count(), self.num_alt_names)

    def test_num_not_und_alternative_names(self):
        self.assertEqual(
            AlternativeName.objects.exclude(language_code='und').count(),
            self.num_not_und_alt_names)


class PostalCodesMixin(object):
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
