import unicodedata
import re

from django.utils.encoding import force_unicode
from django.db.models import signals
from django.db import models
from django.utils.translation import ugettext as _

from south.modelsinspector import add_introspection_rules

import autoslug

from settings import *

__all__ = ['Country', 'Region', 'City', 'CONTINENT_CHOICES', 'to_search',
    'to_ascii']

ALPHA_REGEXP = re.compile('[\W_]+', re.UNICODE)

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


def to_search(value):
    """
    Convert a string value into a string that is usable against
    City.search_names.

    For example, 'Paris Texas' would become 'paristexas'.
    """

    return ALPHA_REGEXP.sub('', to_ascii(value)).lower()


def set_name_ascii(sender, instance=None, **kwargs):
    """
    Signal reciever that sets instance.name_ascii from instance.name.

    Ascii versions of names are often useful for autocompletes and search.
    """
    name_ascii = to_ascii(instance.name)
    if name_ascii and not instance.name_ascii:
        instance.name_ascii = to_ascii(instance.name)


def set_display_name(sender, instance=None, **kwargs):
    """
    Set instance.display_name to instance.get_display_name(), avoid spawning
    queries during __unicode__().
    """
    instance.display_name = instance.get_display_name()


class Base(models.Model):
    """
    Base model with boilerplate for all models.
    """

    name_ascii = models.CharField(max_length=200, blank=True, db_index=True)
    slug = autoslug.AutoSlugField(populate_from='name_ascii')
    geoname_id = models.IntegerField(null=True, blank=True, unique=True)
    alternate_names = models.TextField(null=True, blank=True, default='')

    class Meta:
        abstract = True
        ordering = ['name']

    def __unicode__(self):
        display_name = getattr(self, 'display_name', None)
        if display_name:
            return display_name
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
    display_name = models.CharField(max_length=200)
    geoname_code = models.CharField(max_length=50, null=True, blank=True,
        db_index=True)

    country = models.ForeignKey(Country)

    class Meta:
        unique_together = (('country', 'name'), )
        verbose_name = _('region/state')
        verbose_name_plural = _('regions/states')

    def get_display_name(self):
        return u'%s, %s' % (self.name, self.country.name)

signals.pre_save.connect(set_name_ascii, sender=Region)
signals.pre_save.connect(set_display_name, sender=Region)


class ToSearchTextField(models.TextField):
    """
    Trivial TextField subclass that passes values through to_search
    automatically.
    """
    def get_prep_lookup(self, lookup_type, value):
        """
        Return the value passed through to_search().
        """
        value = super(ToSearchTextField, self).get_prep_lookup(lookup_type,
            value)
        return to_search(value)

    def south_field_triple(self):
        "Returns a suitable description of this field for South."
        from south.modelsinspector import introspector
        field_class = self.__class__.__module__ + "." + self.__class__.__name__
        args, kwargs = introspector(self)
        # That's our definition!
        return (field_class, args, kwargs)


class City(Base):
    """
    City model.
    """

    name = models.CharField(max_length=200, db_index=True)
    display_name = models.CharField(max_length=200)

    search_names = ToSearchTextField(max_length=4000,
        db_index=INDEX_SEARCH_NAMES, blank=True, default='')

    latitude = models.DecimalField(max_digits=8, decimal_places=5,
        null=True, blank=True)
    longitude = models.DecimalField(max_digits=8, decimal_places=5,
        null=True, blank=True)

    region = models.ForeignKey(Region, blank=True, null=True)
    country = models.ForeignKey(Country)

    class Meta:
        unique_together = (('region', 'name'),)
        verbose_name_plural = _(u'cities')

    def get_display_name(self):
        if self.region_id:
            return u'%s, %s, %s' % (self.name, self.region.name,
                self.country.name)
        else:
            return u'%s, %s' % (self.name, self.country.name)
signals.pre_save.connect(set_name_ascii, sender=City)
signals.pre_save.connect(set_display_name, sender=City)


def city_country(sender, instance, **kwargs):
    if instance.region_id and not instance.country_id:
        instance.country = instance.region.country
signals.pre_save.connect(city_country, sender=City)


def city_search_names(sender, instance, **kwargs):
    search_names = []

    country_names = [instance.country.name]
    if instance.country.alternate_names:
        country_names += instance.country.alternate_names.split(',')

    city_names = [instance.name]
    if instance.alternate_names:
        city_names += instance.alternate_names.split(',')

    if instance.region_id:
        region_names = [instance.region.name]
        if instance.region.alternate_names:
            region_names += instance.region.alternate_names.split(',')

    for city_name in city_names:
        for country_name in country_names:
            name = to_search(city_name + country_name)
            if name not in search_names:
                search_names.append(name)

            if instance.region_id:
                for region_name in region_names:
                    name = to_search(city_name + region_name + country_name)
                    if name not in search_names:
                        search_names.append(name)

    instance.search_names = ' '.join(search_names)
signals.pre_save.connect(city_search_names, sender=City)
