import sys
import uuid

try:
    from django.utils.encoding import force_unicode as force_text
except (NameError, ImportError):
    from django.utils.encoding import force_text

from django.utils.encoding import python_2_unicode_compatible
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point

from model_utils import Choices
import swapper

from .conf import (settings, ALTERNATIVE_NAME_TYPES, SLUGIFY_FUNCTION)
from .managers import AlternativeNameManager

__all__ = [
    'Point', 'Continent', 'Country', 'Region', 'Subregion', 'City', 'District',
    'PostalCode', 'AlternativeName',
]


if sys.version_info >= (3, 0):
    unicode = str

slugify_func = SLUGIFY_FUNCTION


class SlugModel(models.Model):
    slug = models.CharField(max_length=255, unique=True)

    class Meta:
        abstract = True

    def slugify(self):
        raise NotImplementedError("Subclasses of Place must implement slugify()")

    def save(self, *args, **kwargs):
        self.slug = slugify_func(self, self.slugify())
        super(SlugModel, self).save(*args, **kwargs)


@python_2_unicode_compatible
class Place(models.Model):
    name = models.CharField(max_length=200, db_index=True, verbose_name="ascii name")
    alt_names = models.ManyToManyField('AlternativeName')

    objects = models.GeoManager()

    class Meta:
        abstract = True

    @property
    def hierarchy(self):
        """Get hierarchy, root first"""
        lst = self.parent.hierarchy if self.parent else []
        lst.append(self)
        return lst

    def get_absolute_url(self):
        return "/".join([place.slug for place in self.hierarchy])

    def __str__(self):
        return force_text(self.name)

    def save(self, *args, **kwargs):
        if hasattr(self, 'clean'):
            self.clean()
        super(Place, self).save(*args, **kwargs)


class BaseContinent(Place, SlugModel):
    code = models.CharField(max_length=2, unique=True, db_index=True)

    def __str__(self):
        return force_text(self.name)

    class Meta:
        abstract = True

    def slugify(self):
        return slugify_func(self, self.name.encode('utf-8'))


class Continent(BaseContinent):
    class Meta(BaseContinent.Meta):
        swappable = swapper.swappable_setting('cities', 'Continent')


class BaseCountry(Place, SlugModel):
    code = models.CharField(max_length=2, db_index=True, unique=True)
    code3 = models.CharField(max_length=3, db_index=True, unique=True)
    population = models.IntegerField()
    area = models.IntegerField(null=True)
    currency = models.CharField(max_length=3, null=True)
    currency_name = models.CharField(max_length=50, blank=True, null=True)
    currency_symbol = models.CharField(max_length=31, blank=True, null=True)
    language_codes = models.CharField(max_length=250, null=True)
    phone = models.CharField(max_length=20)
    continent = models.ForeignKey(swapper.get_model_name('cities', 'Continent'),
                                  null=True, related_name='countries')
    tld = models.CharField(max_length=5, verbose_name='TLD')
    postal_code_format = models.CharField(max_length=127)
    postal_code_regex = models.CharField(max_length=255)
    capital = models.CharField(max_length=100)
    neighbours = models.ManyToManyField("self")

    class Meta:
        abstract = True
        ordering = ['name']
        verbose_name_plural = "countries"

    @property
    def parent(self):
        return None

    def __str__(self):
        return force_text(self.name)

    def clean(self):
        self.tld = self.tld.lower()

    def slugify(self):
        return slugify_func(self, self.name.encode('utf-8'))


class Country(BaseCountry):
    class Meta(BaseCountry.Meta):
        swappable = swapper.swappable_setting('cities', 'Country')


class Region(Place, SlugModel):
    name_std = models.CharField(max_length=200, db_index=True, verbose_name="standard name")
    code = models.CharField(max_length=200, db_index=True)
    country = models.ForeignKey(swapper.get_model_name('cities', 'Country'),
                                related_name='regions')

    class Meta:
        unique_together = (('country', 'name'),)

    @property
    def parent(self):
        return self.country

    def full_code(self):
        return unicode(".".join([self.parent.code, self.code]))

    def slugify(self):
        return slugify_func(self, '{}_({})'.format(
            unicode(self.name.encode('utf-8')),
            unicode(self.full_code().encode('utf-8'))))


class Subregion(Place, SlugModel):
    name_std = models.CharField(max_length=200, db_index=True, verbose_name="standard name")
    code = models.CharField(max_length=200, db_index=True)
    region = models.ForeignKey(Region, related_name='subregions')

    class Meta:
        unique_together = (('region', 'name'),)

    @property
    def parent(self):
        return self.region

    def full_code(self):
        return ".".join([self.parent.parent.code, self.parent.code, self.code])

    def slugify(self):
        return slugify_func(self, unicode('{}_({})').format(
            self.name.encode('utf-8'),
            self.full_code().encode('utf-8')))


class BaseCity(Place, SlugModel):
    name_std = models.CharField(max_length=200, db_index=True, verbose_name="standard name")
    country = models.ForeignKey(swapper.get_model_name('cities', 'Country'),
                                related_name='cities')
    region = models.ForeignKey(Region, null=True, blank=True, related_name='cities')
    subregion = models.ForeignKey(Subregion, null=True, blank=True, related_name='cities')
    location = models.PointField()
    population = models.IntegerField()
    elevation = models.IntegerField(null=True)
    kind = models.CharField(max_length=10)  # http://www.geonames.org/export/codes.html
    timezone = models.CharField(max_length=40)

    class Meta:
        abstract = True
        unique_together = (('country', 'region', 'subregion', 'name'),)
        verbose_name_plural = "cities"

    @property
    def parent(self):
        return self.region

    def slugify(self):
        return slugify_func(self, unicode(self.id))


class City(BaseCity):
    class Meta(BaseCity.Meta):
        swappable = swapper.swappable_setting('cities', 'City')


class District(Place, SlugModel):
    name_std = models.CharField(max_length=200, db_index=True, verbose_name="standard name")
    code = models.CharField(blank=True, db_index=True, max_length=200, null=True)
    location = models.PointField()
    population = models.IntegerField()
    city = models.ForeignKey(swapper.get_model_name('cities', 'City'), related_name='districts')

    class Meta:
        unique_together = (('city', 'name'),)

    @property
    def parent(self):
        return self.city

    def slugify(self):
        return slugify_func(self, unicode(self.id))


@python_2_unicode_compatible
class AlternativeName(SlugModel):
    KIND = Choices(*ALTERNATIVE_NAME_TYPES)

    name = models.CharField(max_length=255)
    kind = models.CharField(max_length=4, choices=KIND, default=KIND.name)
    language_code = models.CharField(max_length=100)
    is_preferred = models.BooleanField(default=False)
    is_short = models.BooleanField(default=False)
    is_colloquial = models.BooleanField(default=False)
    is_historic = models.BooleanField(default=False)

    objects = AlternativeNameManager()

    def __str__(self):
        return "%s (%s)" % (force_text(self.name), force_text(self.language_code))

    def slugify(self):
        return slugify_func(self, unicode(self.id))


@python_2_unicode_compatible
class PostalCode(Place, SlugModel):
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

    class Meta:
        unique_together = (
            ('country', 'region', 'subregion', 'city', 'district', 'name'),
            ('country', 'region_name', 'subregion_name', 'district_name', 'name'),
        )

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

    def slugify(self):
        return slugify_func(self, unicode(self.id))
