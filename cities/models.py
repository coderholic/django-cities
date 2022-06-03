from random import choice
from string import ascii_uppercase, digits

from .conf import (ALTERNATIVE_NAME_TYPES, SLUGIFY_FUNCTION, DJANGO_VERSION)


if DJANGO_VERSION < 4:
    try:
        from django.utils.encoding import force_unicode as force_text
    except (NameError, ImportError):
        from django.utils.encoding import force_text
else:
    from django.utils.encoding import force_str as force_text

from django.db import transaction
from django.contrib.gis.db.models import PointField
from django.db import models
from django.contrib.gis.geos import Point

from model_utils import Choices
import swapper

from .managers import AlternativeNameManager
from .util import unicode_func

__all__ = [
    'Point', 'Continent', 'Country', 'Region', 'Subregion', 'City', 'District',
    'PostalCode', 'AlternativeName',
]


if DJANGO_VERSION < 2:
    from django.contrib.gis.db.models import GeoManager
else:
    from django.db.models import Manager as GeoManager

slugify_func = SLUGIFY_FUNCTION


def SET_NULL_OR_CASCADE(collector, field, sub_objs, using):
    if field.null is True:
        models.SET_NULL(collector, field, sub_objs, using)
    else:
        models.CASCADE(collector, field, sub_objs, using)


class SlugModel(models.Model):
    slug = models.CharField(blank=True, max_length=255, null=True)

    class Meta:
        abstract = True

    def slugify(self):
        raise NotImplementedError("Subclasses of Place must implement slugify()")

    def save(self, *args, **kwargs):
        self.slug = slugify_func(self, self.slugify())
        # If the slug contains the object's ID and we are creating a new object,
        # save it twice: once to get an ID, another to set the object's slug
        if self.slug is None and getattr(self, 'slug_contains_id', False):
            with transaction.atomic():
                # We first give a randomized slug with a prefix just in case
                # users need to find invalid slugs
                self.slug = 'invalid-{}'.format(''.join(choice(ascii_uppercase + digits) for i in range(20)))
                super(SlugModel, self).save(*args, **kwargs)
                self.slug = slugify_func(self, self.slugify())

                # If the 'force_insert' flag was passed, don't pass it again:
                # doing so will attempt to re-insert with the same primary key,
                # which will cause an IntegrityError.
                kwargs.pop('force_insert', None)
                super(SlugModel, self).save(*args, **kwargs)
        else:
            # This is a performance optimization - we avoid the transaction if
            # the self.slug is not None
            super(SlugModel, self).save(*args, **kwargs)


class Place(models.Model):
    name = models.CharField(max_length=200, db_index=True, verbose_name="ascii name")
    alt_names = models.ManyToManyField('AlternativeName')

    objects = GeoManager()

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
        return self.name


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
                                  null=True,
                                  related_name='countries',
                                  on_delete=SET_NULL_OR_CASCADE)
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
        return self.name


class Country(BaseCountry):
    class Meta(BaseCountry.Meta):
        swappable = swapper.swappable_setting('cities', 'Country')


class Region(Place, SlugModel):
    name_std = models.CharField(max_length=200, db_index=True, verbose_name="standard name")
    code = models.CharField(max_length=200, db_index=True)
    country = models.ForeignKey(swapper.get_model_name('cities', 'Country'),
                                related_name='regions',
                                on_delete=SET_NULL_OR_CASCADE)

    class Meta:
        unique_together = (('country', 'name'),)

    @property
    def parent(self):
        return self.country

    def full_code(self):
        return unicode_func(".".join([self.parent.code, self.code]))

    def slugify(self):
        return '{}_({})'.format(
            unicode_func(self.name),
            unicode_func(self.full_code()))


class Subregion(Place, SlugModel):
    slug_contains_id = True

    name_std = models.CharField(max_length=200, db_index=True, verbose_name="standard name")
    code = models.CharField(max_length=200, db_index=True)
    region = models.ForeignKey(Region,
                               related_name='subregions',
                               on_delete=SET_NULL_OR_CASCADE)

    class Meta:
        unique_together = (('region', 'id', 'name'),)

    @property
    def parent(self):
        return self.region

    def full_code(self):
        return ".".join([self.parent.parent.code, self.parent.code, self.code])

    def slugify(self):
        return unicode_func('{}-{}').format(
            unicode_func(self.id),
            unicode_func(self.name))


class BaseCity(Place, SlugModel):
    slug_contains_id = True

    name_std = models.CharField(max_length=200, db_index=True, verbose_name="standard name")
    country = models.ForeignKey(swapper.get_model_name('cities', 'Country'),
                                related_name='cities',
                                on_delete=SET_NULL_OR_CASCADE)
    region = models.ForeignKey(Region,
                               null=True,
                               blank=True,
                               related_name='cities',
                               on_delete=SET_NULL_OR_CASCADE)
    subregion = models.ForeignKey(Subregion,
                                  null=True,
                                  blank=True,
                                  related_name='cities',
                                  on_delete=SET_NULL_OR_CASCADE)
    location = PointField()
    population = models.IntegerField()
    elevation = models.IntegerField(null=True)
    kind = models.CharField(max_length=10)  # http://www.geonames.org/export/codes.html
    timezone = models.CharField(max_length=40)

    class Meta:
        abstract = True
        unique_together = (('country', 'region', 'subregion', 'id', 'name'),)
        verbose_name_plural = "cities"

    @property
    def parent(self):
        return self.region

    def slugify(self):
        if self.id:
            return '{}-{}'.format(self.id, unicode_func(self.name))
        return None


class City(BaseCity):
    class Meta(BaseCity.Meta):
        swappable = swapper.swappable_setting('cities', 'City')


class District(Place, SlugModel):
    slug_contains_id = True

    name_std = models.CharField(max_length=200, db_index=True, verbose_name="standard name")
    code = models.CharField(blank=True, db_index=True, max_length=200, null=True)
    location = PointField()
    population = models.IntegerField()
    city = models.ForeignKey(swapper.get_model_name('cities', 'City'),
                             related_name='districts',
                             on_delete=SET_NULL_OR_CASCADE)

    class Meta:
        unique_together = (('city', 'name'),)

    @property
    def parent(self):
        return self.city

    def slugify(self):
        if self.id:
            return '{}-{}'.format(self.id, unicode_func(self.name))
        return None


class AlternativeName(SlugModel):
    slug_contains_id = True

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
        if self.id:
            return '{}-{}'.format(self.id, unicode_func(self.name))
        return None


class PostalCode(Place, SlugModel):
    slug_contains_id = True

    code = models.CharField(max_length=20)
    location = PointField()

    country = models.ForeignKey(swapper.get_model_name('cities', 'Country'),
                                related_name='postal_codes',
                                on_delete=SET_NULL_OR_CASCADE)

    # Region names for each admin level, region may not exist in DB
    region_name = models.CharField(max_length=100, db_index=True)
    subregion_name = models.CharField(max_length=100, db_index=True)
    district_name = models.CharField(max_length=100, db_index=True)

    region = models.ForeignKey(Region,
                               blank=True,
                               null=True,
                               related_name='postal_codes',
                               on_delete=SET_NULL_OR_CASCADE)
    subregion = models.ForeignKey(Subregion,
                                  blank=True,
                                  null=True,
                                  related_name='postal_codes',
                                  on_delete=SET_NULL_OR_CASCADE)
    city = models.ForeignKey(swapper.get_model_name('cities', 'City'),
                             blank=True,
                             null=True,
                             related_name='postal_codes',
                             on_delete=SET_NULL_OR_CASCADE)
    district = models.ForeignKey(District,
                                 blank=True,
                                 null=True,
                                 related_name='postal_codes',
                                 on_delete=SET_NULL_OR_CASCADE)

    objects = GeoManager()

    class Meta:
        unique_together = (
            ('country', 'region', 'subregion', 'city', 'district', 'name', 'id', 'code'),
            ('country', 'region_name', 'subregion_name', 'district_name', 'name', 'id', 'code'),
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
        if self.id:
            return '{}-{}'.format(self.id, unicode_func(self.code))
        return None
