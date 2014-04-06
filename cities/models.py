from django.utils.encoding import force_unicode
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from conf import settings

__all__ = [
        'Point', 'Country', 'Region', 'Subregion',
        'City', 'District', 'PostalCode', 'AlternativeName', 
]

class Place(models.Model):
    name = models.CharField(max_length=200, db_index=True, verbose_name="ascii name")
    slug = models.CharField(max_length=200)
    alt_names = models.ManyToManyField('AlternativeName')

    objects = models.GeoManager()

    class Meta:
        abstract = True

    @property
    def hierarchy(self):
        """Get hierarchy, root first"""
        list = self.parent.hierarchy if self.parent else []
        list.append(self)
        return list

    def get_absolute_url(self):
        return "/".join([place.slug for place in self.hierarchy])

    def __unicode__(self):
        return force_unicode(self.name)

class Country(Place):
    code = models.CharField(max_length=2, db_index=True)
    code3 = models.CharField(max_length=3, db_index=True)
    population = models.IntegerField()
    area = models.IntegerField(null=True)
    currency = models.CharField(max_length=3, null=True)
    currency_name = models.CharField(max_length=50, null=True)
    languages = models.CharField(max_length=250, null=True)
    phone = models.CharField(max_length=20)
    continent = models.CharField(max_length=2)
    tld = models.CharField(max_length=5)
    capital = models.CharField(max_length=100)
    neighbours = models.ManyToManyField("self")

    class Meta:
        ordering = ['name']
        verbose_name_plural = "countries"

    @property
    def parent(self):
        return None

    def __unicode__(self):
        return force_unicode(self.name)

class Region(Place):
    name_std = models.CharField(max_length=200, db_index=True, verbose_name="standard name")
    code = models.CharField(max_length=200, db_index=True)
    country = models.ForeignKey(Country)

    @property
    def parent(self):
        return self.country

    def full_code(self):
        return ".".join([self.parent.code, self.code])

class Subregion(Place):
    name_std = models.CharField(max_length=200, db_index=True, verbose_name="standard name")
    code = models.CharField(max_length=200, db_index=True)
    region = models.ForeignKey(Region)

    @property
    def parent(self):
        return self.region

    def full_code(self):
        return ".".join([self.parent.parent.code, self.parent.code, self.code])

class City(Place):
    name_std = models.CharField(max_length=200, db_index=True, verbose_name="standard name")
    location = models.PointField()
    population = models.IntegerField()
    region = models.ForeignKey(Region, null=True, blank=True)
    subregion = models.ForeignKey(Subregion, null=True, blank=True)
    country = models.ForeignKey(Country)
    elevation = models.IntegerField(null=True)
    kind = models.CharField(max_length=10) # http://www.geonames.org/export/codes.html
    timezone = models.CharField(max_length=40) 

    class Meta:
        verbose_name_plural = "cities"

    @property
    def parent(self):
        return self.region

class District(Place):
    name_std = models.CharField(max_length=200, db_index=True, verbose_name="standard name")
    location = models.PointField()
    population = models.IntegerField()
    city = models.ForeignKey(City)

    @property
    def parent(self):
        return self.city

class AlternativeName(models.Model):
    name = models.CharField(max_length=256)
    language = models.CharField(max_length=100)
    is_preferred = models.BooleanField(default=False)
    is_short = models.BooleanField(default=False)
    is_colloquial = models.BooleanField(default=False)

    def __unicode__(self):
        return "%s (%s)" % (force_unicode(self.name), force_unicode(self.language))

class PostalCode(Place):
    code = models.CharField(max_length=20)
    location = models.PointField()

    country = models.ForeignKey(Country, related_name = 'postal_codes')

    # Region names for each admin level, region may not exist in DB
    region_name = models.CharField(max_length=100, db_index=True)
    subregion_name = models.CharField(max_length=100, db_index=True)
    district_name = models.CharField(max_length=100, db_index=True)

    objects = models.GeoManager()

    @property
    def parent(self):
        return self.country

    @property
    def name_full(self):
        """Get full name including hierarchy"""
        return u', '.join(reversed(self.names)) 

    @property
    def names(self):
        """Get a hierarchy of non-null names, root first"""
        return [e for e in [
            force_unicode(self.country),
            force_unicode(self.region_name),
            force_unicode(self.subregion_name),
            force_unicode(self.district_name),
            force_unicode(self.name),
        ] if e]

    def __unicode__(self):
        return force_unicode(self.code)
