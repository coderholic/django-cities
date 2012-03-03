import unicodedata

from django.utils.encoding import force_unicode
from django.db.models import signals
from django.db import models
from django.template import defaultfilters
from django.utils.translation import ugettext as _

import autoslug

from settings import *

__all__ = ['Country','City', 'Zip', 'CONTINENT_CHOICES']

CONTINENT_CHOICES = (
    ('OC', _(u'Oceania')),
    ('EU', _(u'Europe')),
    ('AF', _(u'Africa')),
    ('NA', _(u'North America')),
    ('AN', _(u'Antarctica')),
    ('SA', _(u'South America')),
    ('AS', _(u'Asia')),
)

def set_name_ascii(sender, instance=None, **kwargs):
    if isinstance(instance.name, str):
        instance.name = force_unicode(instance.name)

    instance.name_ascii = unicodedata.normalize('NFKD', instance.name
        ).encode('ascii', 'ignore')

class Country(models.Model):
    name = models.CharField(max_length=200, unique=True)
    name_ascii = models.CharField(max_length=200, db_index=True)
    slug = autoslug.AutoSlugField(populate_from='name_ascii')

    code2 = models.CharField(max_length=2, blank=True, unique=True)
    code3 = models.CharField(max_length=3, blank=True, unique=True)
    continent = models.CharField(max_length=2, db_index=True, choices=CONTINENT_CHOICES)
    # can't put it unique because of dupe .gp http://en.wikipedia.org/wiki/.bl
    tld = models.CharField(max_length=5, blank=True, db_index=True)
    
    class Meta:
        verbose_name_plural = _(u'countries')
        ordering = ['name']

    def __unicode__(self):
        return self.name
signals.pre_save.connect(set_name_ascii, sender=Country)

class City(models.Model):
    name = models.CharField(max_length=200, unique=True)
    name_ascii = models.CharField(max_length=200, db_index=True)
    slug = autoslug.AutoSlugField(populate_from='name_ascii', 
        unique_with=('country__name',))
    
    country = models.ForeignKey(Country)

    class Meta:
        unique_together = (('country', 'name'),)
        verbose_name_plural = _(u'cities')
        ordering = ['name']

        if not ENABLE_CITY:
            abstract = True
        
    def __unicode__(self):
        return self.name
signals.pre_save.connect(set_name_ascii, sender=City)

class Zip(models.Model):
    name = models.CharField(max_length=200)
    name_ascii = models.CharField(max_length=200, db_index=True)
    slug = autoslug.AutoSlugField(populate_from='name_ascii', 
        unique_with=('city__name', 'city__country__name',))

    code = models.CharField(max_length=25, db_index=True)
    city = models.ForeignKey('City')
    
    class Meta:
        ordering = ['city', 'code']
        unique_together = (('city', 'code'),)

        if not ENABLE_ZIP:
            abstract = True

    def __unicode__(self):
        return self.code
signals.pre_save.connect(set_name_ascii, sender=Zip)
