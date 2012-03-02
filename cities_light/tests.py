# -*- encoding: utf-8 -*-

from django.utils import unittest

from .models import Country, City

class SaveTestCase(unittest.TestCase):
    def testCountryAsciiAndSlug(self):
        country = Country(name=u'áó éú')
        country.save()

        self.assertEqual(country.name_ascii, u'ao eu')
        self.assertEqual(country.slug, u'ao-eu')

    def testCityAsciiAndSlug(self):
        Country(name=u'foo').save()
        city = City(name=u'áó éú', country_id=1)
        city.save()

        self.assertEqual(city.name_ascii, u'ao eu')
        self.assertEqual(city.slug, u'ao-eu')
