"""Test for models methods."""
from django import test
from django.conf import settings
from django.core.exceptions import ValidationError

from ..loading import get_cities_model
from ..validators import timezone_validator


class TestModels(test.TransactionTestCase):
    """Tests for cities light models methods."""

    longMessage = True

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

    def test_city_search_names_icontains(self):
        """Test for City.search_names space-insensitive lookup."""
        country_model = get_cities_model('Country')
        region_model = get_cities_model('Region')
        subregion_model = get_cities_model('SubRegion')
        city_model = get_cities_model('City')

        country = country_model(
            name='Country',
            name_ascii='Country',
            geoname_id='123456',
            continent='EU')
        country.save()

        region = region_model(
            name='Region',
            name_ascii='Region',
            geoname_id='123457',
            display_name='Region',
            country=country
        )
        region.save()

        subregion = subregion_model(
            name='SubRegion',
            name_ascii='SubRegion',
            geoname_id='987654',
            display_name='SubRegion',
            region=region,
            country=country
        )
        subregion.save()

        city1 = city_model(
            name='First City',
            name_ascii='First City',
            geoname_id='123458',
            display_name='First City',
            search_names='firstcityregioncountry',
            region=region,
            country=country,
            subregion=subregion
        )
        city1.save()

        city2 = city_model(
            name='Second City',
            name_ascii='Second City',
            geoname_id='123459',
            display_name='Second City',
            search_names='secondcityregioncountry',
            region=region,
            country=country,
            subregion=subregion
        )
        city2.save()

        city_qs = city_model.objects.filter(
            search_names__icontains='First City'
        )

        self.assertEqual(len(city_qs), 1, msg='Should find 1 city')
        self.assertEqual(city_qs[0].name, city1.name)

        city_qs = city_model.objects.filter(
            search_names__icontains='Second City'
        )

        self.assertEqual(len(city_qs), 1, msg='Should find 1 city')
        self.assertEqual(city_qs[0].name, city2.name)

        city_qs = city_model.objects.filter(
            search_names__icontains='Third City'
        )
        self.assertEqual(len(city_qs), 0, msg='Should find 0 cities')

        city_qs = city_model.objects.filter(
            search_names__icontains='Region Country'
        )
        self.assertEqual(len(city_qs), 2, msg='Should find 2 cities')
        self.assertEqual(city_qs[0].name, city1.name)
        self.assertEqual(city_qs[1].name, city2.name)

        city_qs = city_model.objects.filter(
            search_names__icontains='gion coun'
        )
        self.assertEqual(len(city_qs), 2, msg='Should find 2 cities')
        self.assertEqual(city_qs[0].name, city1.name)
        self.assertEqual(city_qs[1].name, city2.name)
