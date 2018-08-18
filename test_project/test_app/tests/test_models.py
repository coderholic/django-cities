from django.contrib.gis.geos import Point
from django.test import TestCase

from cities import models


class SlugModelTest(object):
    """
    Common tests for SlugModel subclasses.
    """

    def instantiate(self):
        """
        Implement this to return a valid instance of the model under test.
        """
        raise NotImplementedError

    def test_save(self):
        instance = self.instantiate()
        instance.save()

    def test_save_force_insert(self):
        """
        Regression test: save() with force_insert=True should work.
        """
        instance = self.instantiate()
        instance.save(force_insert=True)


class ContinentTestCase(SlugModelTest, TestCase):

    def instantiate(self):
        return models.Continent()


class CountryTestCase(SlugModelTest, TestCase):

    def instantiate(self):
        return models.Country(
            population=0,
        )


class RegionTestCase(SlugModelTest, TestCase):

    def instantiate(self):
        country = models.Country(
            population=0
        )
        country.save()
        return models.Region(
            country=country,
        )


class SubregionTestCase(SlugModelTest, TestCase):

    def instantiate(self):
        country = models.Country(
            population=0
        )
        country.save()
        region = models.Region(
            country=country,
        )
        region.save()
        return models.Subregion(
            region=region,
        )


class CityTestCase(SlugModelTest, TestCase):

    def instantiate(self):
        country = models.Country(
            population=0
        )
        country.save()
        return models.City(
            country=country,
            location=Point(0, 0),
            population=0,
        )


class DistrictTestCase(SlugModelTest, TestCase):

    def instantiate(self):
        country = models.Country(
            population=0
        )
        country.save()
        city = models.City(
            country=country,
            location=Point(0, 0),
            population=0,
        )
        city.save()
        return models.District(
            location=Point(0, 0),
            population=0,
            city=city,
        )


class AlternativeNameTestCase(SlugModelTest, TestCase):

    def instantiate(self):
        return models.AlternativeName()


class PostalCodeTestCase(SlugModelTest, TestCase):

    def instantiate(self):
        country = models.Country(
            population=0
        )
        country.save()
        return models.PostalCode(
            location=Point(0, 0),
            country=country,
        )
