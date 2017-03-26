"""Test for models methods."""
from __future__ import unicode_literals

from django import test
from django.conf import settings
from django.core.exceptions import ValidationError

from ..loading import get_cities_model
from ..validators import timezone_validator


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

        city = city_model(
            geoname_id='123457',
            name='city',
            timezone=None
        )
        self.assertEqual(city.get_timezone_info().zone, settings.TIME_ZONE)

        city = city_model(
            geoname_id='123457',
            name='city',
            timezone=''
        )
        self.assertEqual(city.get_timezone_info().zone, settings.TIME_ZONE)

    def test_timezone_validator(self):
        """Test timezone_validator."""
        with self.assertRaises(ValidationError) as e:
            timezone_validator(None)
        self.assertEqual(
            e.exception.messages[0], 'Timezone validation error: None')
        self.assertEqual(e.exception.code, 'timezone_error')

        with self.assertRaises(ValidationError) as e:
            timezone_validator('')
        self.assertEqual(
            e.exception.messages[0], 'Timezone validation error: ')
        self.assertEqual(e.exception.code, 'timezone_error')

        with self.assertRaises(ValidationError) as e:
            timezone_validator('Mars/Cidonia')
        self.assertEqual(
            e.exception.messages[0], 'Timezone validation error: Mars/Cidonia')
        self.assertEqual(e.exception.code, 'timezone_error')

        try:
            value = 'Asia/Novokuznetsk'
            timezone_validator(value)
        except Exception:
            self.assertTrue(
                False,
                'Error call timezone_validator with true value: %s' % value)
