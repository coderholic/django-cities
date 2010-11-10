from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.contrib import admin

# Create your models here.
class Country(models.Model):
	name = models.CharField(max_length = 200)
	slug = models.CharField(max_length = 200, unique=True)
	code = models.CharField(max_length = 2, db_index=True)
	population = models.IntegerField()
	continent = models.CharField(max_length = 2)
	tld = models.CharField(max_length = 10)

	objects = models.GeoManager()

	def __unicode__(self):
		return self.name

class City(models.Model):
	name = models.CharField(max_length = 200)
	slug = models.CharField(max_length = 200, db_index=True)
	country = models.ForeignKey(Country)
	location = models.PointField()
	population = models.IntegerField()

	objects = models.GeoManager()

	def __unicode__(self):
		return "%s, %s" % (self.name, self.country.name)

class Section(models.Model):
	name = models.CharField(max_length = 200)
	slug = models.CharField(max_length = 200)
	city = models.ForeignKey(City)
	location = models.PointField()
	population = models.IntegerField()

	objects = models.GeoManager()

	def __unicode__(self):
		return "%s, %s, %s" % (self.name, self.city.name, self.city.country.name)

admin.site.register(Country)
admin.site.register(City)
admin.site.register(Section)