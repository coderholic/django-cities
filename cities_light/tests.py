# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

from django.utils import unittest

from .forms import CountryForm, CityForm
from .models import Country, City


class FormTestCase(unittest.TestCase):
    def testCountryFormNameAndContinentAlone(self):
        form = CountryForm({'name': 'Spain', 'continent': 'EU'})
        self.assertTrue(form.is_valid())
        form.save()

    def testCityFormNameAndCountryAlone(self):
        country = Country(name='France')
        country.save()
        form = CityForm({'name': 'Paris', 'country': country.pk})
        self.assertTrue(form.is_valid())
        form.save()


class SaveTestCase(unittest.TestCase):
    def testCountryAsciiAndSlug(self):
        country = Country(name='áó éú')
        country.save()

        self.assertEqual(country.name_ascii, 'ao e')
        self.assertEqual(country.slug, 'ao-e')

    def testCityAsciiAndSlug(self):
        city = City(name='áó éú', country_id=1)
        city.save()

        self.assertEqual(city.name_ascii, 'ao e')
        self.assertEqual(city.slug, 'ao-e')
