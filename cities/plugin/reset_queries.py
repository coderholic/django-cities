# -*- coding: utf-8 -*-

"""Call django.db.reset_queries randomly. Default chance is 0.000002 (0.0002%).

This plugin may be useful when processing all geonames database.
To process all geonames database and include cities that do not specify population
or when their population is less than 1000 people use following settings:

CITIES_FILES = {
    'city': {
       'filename': 'allCountries.zip',
       'urls':     ['http://download.geonames.org/export/dump/'+'{filename}']
    },
}

Settings variable CITIES_PLUGINS_RESET_QUERIES_CHANCE may be used to override
default chance:

CITIES_PLUGINS_RESET_QUERIES_CHANCE = 1.0 / 1000000

"""

import random

from django.db import reset_queries
from django.conf import settings

reset_chance = getattr(settings, 'CITIES_PLUGINS_RESET_QUERIES_CHANCE', 0.000002)


class Plugin:

    def random_reset(self):
        if random.random() <= reset_chance:
            reset_queries()

    def city_post(self, parser, city, item):
        self.random_reset()

    def district_post(self, parser, district, item):
        self.random_reset()
