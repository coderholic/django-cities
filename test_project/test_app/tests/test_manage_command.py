# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from unittest import skipIf

from django import VERSION as django_version
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.test.signals import setting_changed

from cities.models import (Country, Region, Subregion, City, District,
                           PostalCode, AlternativeName)

from ..mixins import (
    NoInvalidSlugsMixin, CountriesMixin, RegionsMixin, SubregionsMixin,
    CitiesMixin, DistrictsMixin, AlternativeNamesMixin, PostalCodesMixin)
from ..utils import reload_cities_settings


setting_changed.connect(reload_cities_settings, dispatch_uid='reload_cities_settings')


@override_settings(CITIES_SKIP_CITIES_WITH_EMPTY_REGIONS=True)
class SkipCitiesWithEmptyRegionsManageCommandTestCase(
        NoInvalidSlugsMixin, CountriesMixin, RegionsMixin, SubregionsMixin,
        CitiesMixin, DistrictsMixin, TestCase):
    num_countries = 250
    num_regions = 171
    num_ad_regions = 7
    num_ua_regions = 27
    num_subregions = 4928
    num_cities = 117
    num_ua_cities = 50
    num_districts = 3

    @classmethod
    def setUpTestData(cls):
        # Run the import command only once
        super(SkipCitiesWithEmptyRegionsManageCommandTestCase, cls).setUpTestData()
        call_command('cities', force=True, **{
            'import': 'country,region,subregion,city,district',
        })
        cls.counts = {
            'countries': Country.objects.count(),
            'regions': Region.objects.count(),
            'subregions': Subregion.objects.count(),
            'cities': City.objects.count(),
            'districts': District.objects.count(),
            'postal_codes': PostalCode.objects.count(),
        }


class ManageCommandTestCase(
        NoInvalidSlugsMixin, CountriesMixin, RegionsMixin, SubregionsMixin,
        CitiesMixin, DistrictsMixin, AlternativeNamesMixin, PostalCodesMixin,
        TestCase):
    num_countries = 250
    num_regions = 171
    num_ad_regions = 7
    num_ua_regions = 27
    num_subregions = 4928
    num_cities = 121
    num_ua_cities = 50
    num_districts = 3
    num_alt_names = 2945
    num_not_und_alt_names = 579
    num_postal_codes = 13

    @classmethod
    def setUpTestData(cls):
        # Run the import command only once
        super(ManageCommandTestCase, cls).setUpTestData()
        call_command('cities', force=True, **{
            'import': 'country,region,subregion,city,district,alt_name,postal_code',
        })
        cls.counts = {
            'countries': Country.objects.count(),
            'regions': Region.objects.count(),
            'subregions': Subregion.objects.count(),
            'cities': City.objects.count(),
            'districts': District.objects.count(),
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
        self.assertEqual(District.objects.count(), self.counts['districts'])
        self.assertEqual(AlternativeName.objects.count(), self.counts['alt_names'])
        self.assertEqual(PostalCode.objects.count(), self.counts['postal_codes'])


# This was tested manually
@skipIf(django_version < (1, 8), "Django < 1.8, skipping test with CITIES_LOCALES=['all']")
@override_settings(CITIES_LOCALES=['all'])
class AllLocalesManageCommandTestCase(
        NoInvalidSlugsMixin, CountriesMixin, RegionsMixin, SubregionsMixin,
        CitiesMixin, DistrictsMixin, AlternativeNamesMixin, TestCase):
    num_countries = 250
    num_regions = 171
    num_ad_regions = 7
    num_ua_regions = 27
    num_subregions = 4928
    num_cities = 121
    num_ua_cities = 50
    num_districts = 3
    num_alt_names = 7760
    num_not_und_alt_names = 5394

    @classmethod
    def setUpTestData(cls):
        # Run the import command only once
        super(AllLocalesManageCommandTestCase, cls).setUpTestData()
        call_command('cities', force=True, **{
            'import': 'country,region,subregion,city,district,alt_name',
        })
        cls.counts = {
            'countries': Country.objects.count(),
            'regions': Region.objects.count(),
            'subregions': Subregion.objects.count(),
            'cities': City.objects.count(),
            'districts': District.objects.count(),
            'alt_names': AlternativeName.objects.count(),
        }
