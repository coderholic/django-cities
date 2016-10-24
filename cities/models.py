try:
    from django.utils.encoding import force_unicode as force_text
except (NameError, ImportError):
    from django.utils.encoding import force_text

from django.utils.encoding import python_2_unicode_compatible
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point

import swapper

from .conf import settings

__all__ = [
    'Point', 'Continent', 'Country', 'Region', 'Subregion',
    'City', 'District', 'PostalCode', 'AlternativeName',
]


@python_2_unicode_compatible
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

    def __str__(self):
        return force_text(self.name)


class BaseContinent(Place):
    code = models.CharField(max_length=2, unique=True, db_index=True)

    def __str__(self):
        return force_text(self.name)

    class Meta:
        abstract = True


class Continent(BaseContinent):
    class Meta(BaseContinent.Meta):
        swappable = swapper.swappable_setting('cities', 'Continent')


class BaseCountry(Place):
    code = models.CharField(max_length=2, db_index=True)
    code3 = models.CharField(max_length=3, db_index=True)
    population = models.IntegerField()
    area = models.IntegerField(null=True)
    currency = models.CharField(max_length=3, null=True)
    currency_name = models.CharField(max_length=50, null=True)
    language_codes = models.CharField(max_length=250, null=True)
    phone = models.CharField(max_length=20)
    continent = models.ForeignKey(swapper.get_model_name('cities', 'Continent'),
                                  null=True, related_name='countries')
    tld = models.CharField(max_length=5, verbose_name='TLD')
    capital = models.CharField(max_length=100)
    neighbours = models.ManyToManyField("self")

    class Meta:
        abstract = True
        ordering = ['name']
        verbose_name_plural = "countries"

    @property
    def parent(self):
        return None


class Country(BaseCountry):
    class Meta(BaseCountry.Meta):
        swappable = swapper.swappable_setting('cities', 'Country')


class Region(Place):
    name_std = models.CharField(max_length=200, db_index=True, verbose_name="standard name")
    code = models.CharField(max_length=200, db_index=True)
    country = models.ForeignKey(swapper.get_model_name('cities', 'Country'),
                                related_name='regions')

    @property
    def parent(self):
        return self.country

    def full_code(self):
        return ".".join([self.parent.code, self.code])


class Subregion(Place):
    name_std = models.CharField(max_length=200, db_index=True, verbose_name="standard name")
    code = models.CharField(max_length=200, db_index=True)
    region = models.ForeignKey(Region, related_name='subregions')

    @property
    def parent(self):
        return self.region

    def full_code(self):
        return ".".join([self.parent.parent.code, self.parent.code, self.code])


class BaseCity(Place):
    name_std = models.CharField(max_length=200, db_index=True, verbose_name="standard name")
    location = models.PointField()
    population = models.IntegerField()
    region = models.ForeignKey(Region, null=True, blank=True, related_name='cities')
    subregion = models.ForeignKey(Subregion, null=True, blank=True, related_name='cities')
    country = models.ForeignKey(swapper.get_model_name('cities', 'Country'),
                                related_name='cities')
    elevation = models.IntegerField(null=True)
    kind = models.CharField(max_length=10)  # http://www.geonames.org/export/codes.html
    timezone = models.CharField(max_length=40)

    class Meta:
        abstract = True
        verbose_name_plural = "cities"

    @property
    def parent(self):
        return self.region


class City(BaseCity):
    class Meta(BaseCity.Meta):
        swappable = swapper.swappable_setting('cities', 'City')


class District(Place):
    name_std = models.CharField(max_length=200, db_index=True, verbose_name="standard name")
    location = models.PointField()
    population = models.IntegerField()
    city = models.ForeignKey(swapper.get_model_name('cities', 'City'), related_name='districts')

    @property
    def parent(self):
        return self.city


@python_2_unicode_compatible
class AlternativeName(models.Model):
    name = models.CharField(max_length=256)
    language_code = models.CharField(max_length=100)
    is_preferred = models.BooleanField(default=False)
    is_short = models.BooleanField(default=False)
    is_colloquial = models.BooleanField(default=False)

    def __str__(self):
        return "%s (%s)" % (force_text(self.name), force_text(self.language_code))


@python_2_unicode_compatible
class PostalCode(Place):
    code = models.CharField(max_length=20)
    location = models.PointField()

    country = models.ForeignKey(swapper.get_model_name('cities', 'Country'),
                                related_name='postal_codes')

    # Region names for each admin level, region may not exist in DB
    region_name = models.CharField(max_length=100, db_index=True)
    subregion_name = models.CharField(max_length=100, db_index=True)
    district_name = models.CharField(max_length=100, db_index=True)

    region = models.ForeignKey(Region, blank=True, null=True, related_name='postal_codes')
    subregion = models.ForeignKey(Subregion, blank=True, null=True, related_name='postal_codes')
    city = models.ForeignKey(swapper.get_model_name('cities', 'City'),
                             blank=True, null=True, related_name='postal_codes')
    district = models.ForeignKey(District, blank=True, null=True, related_name='postal_codes')

    objects = models.GeoManager()

    @property
    def parent(self):
        return self.country

    @property
    def name_full(self):
        """Get full name including hierarchy"""
        return force_text(', '.join(reversed(self.names)))

    @property
    def names(self):
        """Get a hierarchy of non-null names, root first"""
        return [e for e in [
            force_text(self.country),
            force_text(self.region_name),
            force_text(self.subregion_name),
            force_text(self.district_name),
            force_text(self.name),
        ] if e]

    def __str__(self):
        return force_text(self.code)
