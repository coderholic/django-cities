import unicodedata

#not sure why he needed force_unicode, leaving it here as a reminder
#from django.utils.encoding import force_unicode
from django.db.models import signals
from django.db import models
from django.template import defaultfilters

__all__ = ['Country','City']

def ascii_name_and_slug(sender, instance=None, **kwargs):
    if isinstance(instance.name, str):
        instance.name = unicode(instance.name)

    instance.name_ascii = unicodedata.normalize('NFKD', instance.name
        ).encode('ascii', 'ignore')

    instance.slug = defaultfilters.slugify(instance.name_ascii)

class Country(models.Model):
    name = models.CharField(max_length=200, db_index=True, 
        verbose_name="standard name")
    name_ascii = models.CharField(max_length=200, db_index=True, 
        verbose_name="ascii name", blank=True)
    slug = models.CharField(max_length=200, blank=True)
    code2 = models.CharField(max_length=2, db_index=True, null=True, blank=True)
    continent = models.CharField(max_length=2)
    tld = models.CharField(max_length=5, null=True, blank=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = "countries"

    def __unicode__(self):
        return self.name
signals.pre_save.connect(ascii_name_and_slug, sender=Country)

class City(models.Model):
    name = models.CharField(max_length=200, db_index=True, 
        verbose_name="standard name")
    name_ascii = models.CharField(max_length=200, db_index=True, 
        verbose_name="ascii name", blank=True)
    slug = models.CharField(max_length=200, blank=True)
    country = models.ForeignKey(Country)
    postal_code = models.CharField(max_length=7, null=True, blank=True)

    class Meta:
        verbose_name_plural = "cities"
        
    def __unicode__(self):
        return self.name
signals.pre_save.connect(ascii_name_and_slug, sender=City) 
