# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase, override_settings
from django.test.signals import setting_changed

from ..mixins import NoInvalidSlugsMixin, ContinentsMixin
from ..utils import reload_continent_data


setting_changed.connect(reload_continent_data, dispatch_uid='reload_continent_data')


class DefaultContinentData(
        NoInvalidSlugsMixin, ContinentsMixin, TestCase):
    num_continents = 7


@override_settings(CITIES_CONTINENT_DATA={
    'AF': ('Africa', 6255146),
    'EA': ('Eurasia', 6255148),
    'NA': ('North America', 6255149),
    'OC': ('Oceania', 6255151),
    'SA': ('South America', 6255150),
    'AN': ('Antarctica', 6255152),
})
class EurasianContinentData(
        NoInvalidSlugsMixin, ContinentsMixin, TestCase):
    num_continents = 6


@override_settings(CITIES_CONTINENT_DATA={
    'AF': ('Africa', 6255146),
    'AS': ('Asia', 6255147),
    'EU': ('Europe', 6255148),
    'AM': ('America', 6255149),
    'OC': ('Oceania', 6255151),
    'AN': ('Antarctica', 6255152),
})
class AmericanContinentData(
        NoInvalidSlugsMixin, ContinentsMixin, TestCase):
    num_continents = 6


@override_settings(CITIES_CONTINENT_DATA={
    'AF': ('Africa', 6255146),
    'EA': ('Eurasia', 6255148),
    'NA': ('North America', 6255149),
    'OC': ('Oceania', 6255151),
    'SA': ('South America', 6255150),
})
class NoAntarcticaContinentData(
        NoInvalidSlugsMixin, ContinentsMixin, TestCase):
    num_continents = 5


@override_settings(CITIES_CONTINENT_DATA={
    'AE': ('Afroeurasia', 6255148),
    'AM': ('America', 6255149),
    'OC': ('Oceania', 6255151),
    'AN': ('Antarctica', 6255152),
})
class AfroEurasianContinentData(
        NoInvalidSlugsMixin, ContinentsMixin, TestCase):
    num_continents = 4
