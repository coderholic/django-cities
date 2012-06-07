import unicodedata

from django.utils.encoding import force_unicode
from django.db.models import signals
from django.db import models
from django.utils.translation import ugettext as _

import autoslug

from settings import *

__all__ = ['Country', 'Region', 'City', 'CONTINENT_CHOICES']

CONTINENT_CHOICES = (
    ('OC', _(u'Oceania')),
    ('EU', _(u'Europe')),
    ('AF', _(u'Africa')),
    ('NA', _(u'North America')),
    ('AN', _(u'Antarctica')),
    ('SA', _(u'South America')),
    ('AS', _(u'Asia')),
)

def to_ascii(value):
    if isinstance(value, str):
        value = force_unicode(value)

    return unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')


def set_name_ascii(sender, instance=None, **kwargs):
    """
    Signal reciever that sets instance.name_ascii from instance.name.

    Ascii versions of names are often useful for autocompletes and search.
    """
    instance.name_ascii = to_ascii(instance.name)


class Base(models.Model):
    """
    Base model with boilerplate for all models.
    """

    name_ascii = models.CharField(max_length=200, blank=True, db_index=True)
    slug = autoslug.AutoSlugField(populate_from='name_ascii')
    geoname_id = models.IntegerField(null=True, blank=True)
    alternate_names = models.TextField(null=True, blank=True, default='')

    class Meta:
        abstract = True
        ordering = ['name']

    def __unicode__(self):
        return self.name


class Country(Base):
    """
    Country model.
    """

    name = models.CharField(max_length=200, unique=True)

    code2 = models.CharField(max_length=2, null=True, blank=True, unique=True)
    code3 = models.CharField(max_length=3, null=True, blank=True, unique=True)
    continent = models.CharField(max_length=2, db_index=True,
        choices=CONTINENT_CHOICES)
    tld = models.CharField(max_length=5, blank=True, db_index=True)

    class Meta:
        verbose_name_plural = _(u'countries')
signals.pre_save.connect(set_name_ascii, sender=Country)


class Region(Base):
    """
    Region/State model.
    """

    name = models.CharField(max_length=200, db_index=True)
    geoname_code = models.CharField(max_length=50, null=True, blank=True,
        db_index=True)

    country = models.ForeignKey(Country)

    class Meta:
        unique_together = (('country', 'name'), )
        verbose_name = _('region/state')
        verbose_name_plural = _('regions/states')
signals.pre_save.connect(set_name_ascii, sender=Region)


class City(Base):
    """
    City model.
    """

    name = models.CharField(max_length=200, db_index=True)

    search_names = models.TextField(max_length=4000, db_index=True, blank=True,
        default='')

    latitude = models.DecimalField(max_digits=8, decimal_places=5,
        null=True, blank=True)
    longitude = models.DecimalField(max_digits=8, decimal_places=5,
        null=True, blank=True)

    region = models.ForeignKey(Region, null=True)
    country = models.ForeignKey(Country)

    class Meta:
        unique_together = (('region', 'name'),)
        verbose_name_plural = _(u'cities')
signals.pre_save.connect(set_name_ascii, sender=City)


def city_country(sender, instance, **kwargs):
    if instance.region_id and not instance.country_id:
        instance.country = instance.region.country
signals.pre_save.connect(city_country, sender=City)
