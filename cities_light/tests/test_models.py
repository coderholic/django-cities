"""Test for models methods."""
from __future__ import unicode_literals

from django import test
from django.conf import settings
from ..loading import get_cities_model


class TestModels(test.TransactionTestCase):
    """Tests for cities light models methods."""

    def test_city_get_timezone(self):
        """Test City.get_timezone_info method."""
        city_model = get_cities_model('City')

        city = city_model(
            geoname_id='123456',
            name='city',
            timezone='Asia/Novosibirsk'
        )
        self.assertEqual(city.get_timezone_info().zone, 'Asia/Novosibirsk')

        city = city_model(
            geoname_id='123457',
            name='city',
            timezone='Mars/Cidonia'
        )
        self.assertEqual(city.get_timezone_info().zone, settings.TIME_ZONE)
