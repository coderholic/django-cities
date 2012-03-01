#not sure why he needed force_unicode, leaving it here as a reminder
#from django.utils.encoding import force_unicode
from django.db import models
from conf import settings
from util import create_model, un_camel
    
__all__ = ['Country','City']

class Country(models.Model):
    name = models.CharField(max_length=200, db_index=True, verbose_name="ascii name")
    slug = models.CharField(max_length=200)
    code = models.CharField(max_length=2, db_index=True)
    population = models.IntegerField()
    continent = models.CharField(max_length=2)
    tld = models.CharField(max_length=5)
    objects = models.GeoManager()
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = "countries"

    def __unicode__(self):
        return self.name

class City(models.Model):
    name = models.CharField(max_length=200, db_index=True, verbose_name="ascii name")
    name_std = models.CharField(max_length=200, db_index=True, verbose_name="standard name")
    slug = models.CharField(max_length=200)
    country = models.ForeignKey(Country)
    population = models.IntegerField()
    postal_code = models.CharField(max_length=7, null=True, blank=True)

    class Meta:
        verbose_name_plural = "cities"
        
    def __unicode__(self):
        return self.name
