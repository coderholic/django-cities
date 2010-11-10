#!/usr/bin/env python
"""
GeoNames city data import script. Requires the following files:
- http://download.geonames.org/export/dump/countryInfo.txt
- http://download.geonames.org/export/dump/cities1000.zip
Based on Richard Crowley's Django Shell Script https://gist.github.com/79156

Part of django-cities by Ben Dowling
"""

import os
import sys
sys.path[0] = os.path.normpath(os.path.join(sys.path[0], '..', '.'))
from django.core.management import setup_environ
import settings
setup_environ(settings)
import datetime
from friends.models import Friendship
from friends.views import friendship_request
from django.contrib.gis.geos import Point
from django.template.defaultfilters import slugify
from cities.models import *
import codecs

def import_countries():
	for line in open("countryInfo.txt"):
		if line[0] == "#":
			continue

		items = line.split("\t")
		country = Country()
		country.code = items[0]
		country.name = items[4]
		country.slug = slugify(country.name)
		country.population = items[7]
		country.continent = items[8]
		country.tld = items[9]
		country.save()

		print "Added country %s" % country.name

def import_cities():
	for line in codecs.open("cities1000.txt", "r", "utf-8"):
		if line[0] == "#":
			continue

		items = line.split("\t")
		print items
		admin_type = items[11]
		type = items[7]

		# See http://www.geonames.org/export/codes.html
		if type in ['PPL', 'PPLA', 'PPLC', 'PPLA2', 'PPLA3', 'PPLA4'] and (type == 'PPLC' or admin_type != 'GLA'):
			city = City()
			city.id = items[0]
			city.name = items[1]
			city.slug = slugify(city.name)
			city.location = Point(float(items[4]), float(items[5]))
			city.population = items[14]
			city.country = Country.objects.get(code=items[8])
			city.save()
			print "Added city %s" % city

def import_sections():
	for line in codecs.open("cities1000.txt", "r", "utf-8"):
		if line[0] == "#":
			continue

		items = line.split("\t")

		admin_type = items[11]
		type = items[7]

		# See http://www.geonames.org/export/codes.html
		if type == 'PPLX' or (admin_type == 'GLA' and type != 'PPLC'):
			section = Section()
			section.id = items[0]
			section.name = items[1]
			section.slug = slugify(section.name)
			section.location = Point(float(items[4]), float(items[5]))
			section.population = items[14]
			section.city = City.objects.filter(population__gt=150000).distance(section.location).order_by('distance')[0] # Set the nearest city
			section.save()
			print "Added section %s" % section

if '__main__' == __name__:
	import_sections()