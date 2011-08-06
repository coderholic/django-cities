from django.contrib.gis.db import models
from django.contrib.gis.geos import Point

class Country(models.Model):
	name = models.CharField(max_length = 200)
	code = models.CharField(max_length = 2, db_index=True)
	population = models.IntegerField()
	continent = models.CharField(max_length = 2)
	tld = models.CharField(max_length = 5, unique=True)

	objects = models.GeoManager()

	def __unicode__(self):
		return self.name

	@property
	def hierarchy(self):
		return [self]

	class Meta:
		ordering = ['name']

class Region(models.Model):
	name = models.CharField(max_length = 200)
	slug = models.CharField(max_length = 200, db_index=True)
	code = models.CharField(max_length = 10, db_index=True)
	country = models.ForeignKey(Country)
	objects = models.GeoManager()

	def __unicode__(self):
		return "%s, %s" % (self.name, self.country)

	@property
	def hierarchy(self):
		list = self.country.hierarchy
		list.append(self)
		return list

class CityManager(models.GeoManager):
	def nearest_to(self, lat, lon):
		#Wrong x y order
		#p = Point(float(lat), float(lon))
		p = Point(float(lon), float(lat))
		return self.nearest_to_point(p)

	def nearest_to_point(self, point):
		return self.distance(point).order_by('distance')[0]

class City(models.Model):
	name = models.CharField(max_length = 200)
	slug = models.CharField(max_length = 200, db_index=True)
	region = models.ForeignKey(Region)
	location = models.PointField()
	population = models.IntegerField()

	objects = CityManager()

	def __unicode__(self):
		return "%s, %s" % (self.name, self.region)

	@property
	def hierarchy(self):
		list = self.region.hierarchy
		list.append(self)
		return list

class District(models.Model):
	name = models.CharField(max_length = 200)
	slug = models.CharField(max_length = 200, db_index=True)
	city = models.ForeignKey(City)
	location = models.PointField()
	population = models.IntegerField()

	objects = models.GeoManager()

	def __unicode__(self):
		return u"%s, %s" % (self.name, self.city)

	@property
	def hierarchy(self):
		list = self.city.hierarchy
		list.append(self)
		return list
