from django.utils.encoding import force_unicode
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from conf import settings
from util import create_model, un_camel
    
__all__ = ['Point','Country','Region','City','District','geo_alt_names','postal_codes']

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

    @property
    def parent(self):
        return None
        
    @property
    def hierarchy(self):
        """Get hierarchy, root first"""
        return [self]
        
    def __unicode__(self):
        return force_unicode(self.name)

class Region(models.Model):
    name = models.CharField(max_length=200, db_index=True, verbose_name="ascii name")
    name_std = models.CharField(max_length=200, db_index=True, verbose_name="standard name")
    slug = models.CharField(max_length=200)
    code = models.CharField(max_length=200, db_index=True)
    level = models.IntegerField(db_index=True, verbose_name="admin level")  # Level 0 has no parent region
    region_parent = models.ForeignKey('self', null=True, blank=True, related_name='region_children')
    country = models.ForeignKey(Country)
    objects = models.GeoManager()

    @property
    def parent(self):
        """Returns parent region if available, otherwise country"""
        return self.region_parent if self.region_parent else self.country
        
    @property
    def hierarchy(self):
        """Get hierarchy, root first"""
        list = self.parent.hierarchy
        list.append(self)
        return list
        
    def __unicode__(self):
        return u'{}, {}'.format(force_unicode(self.name_std), self.parent)    
        
class City(models.Model):
    name = models.CharField(max_length=200, db_index=True, verbose_name="ascii name")
    name_std = models.CharField(max_length=200, db_index=True, verbose_name="standard name")
    slug = models.CharField(max_length=200)
    region = models.ForeignKey(Region, null=True, blank=True)
    country = models.ForeignKey(Country)
    location = models.PointField()
    population = models.IntegerField()
    objects = models.GeoManager()

    class Meta:
        verbose_name_plural = "cities"
        
    @property
    def parent(self):
        """Returns region if available, otherwise country"""
        return self.region if self.region else self.country
        
    @property
    def hierarchy(self):
        """Get hierarchy, root first"""
        list = self.parent.hierarchy
        list.append(self)
        return list
        
    def __unicode__(self):
        return u'{}, {}'.format(force_unicode(self.name_std), self.parent)

class District(models.Model):
    name = models.CharField(max_length=200, db_index=True, verbose_name="ascii name")
    name_std = models.CharField(max_length=200, db_index=True, verbose_name="standard name")
    slug = models.CharField(max_length=200)
    city = models.ForeignKey(City)
    location = models.PointField()
    population = models.IntegerField()
    objects = models.GeoManager()
    
    @property
    def parent(self):
        return self.city
        
    @property
    def hierarchy(self):
        """Get hierarchy, root first"""
        list = self.parent.hierarchy
        list.append(self)
        return list
        
    def __unicode__(self):
        return u'{}, {}'.format(force_unicode(self.name_std), self.parent)

class GeoAltNameManager(models.GeoManager):
    def get_preferred(self, default=None, **kwargs):
        """
        If multiple names are available, get the preferred, otherwise return any existing or the default.
        Extra keywords can be provided to further filter the names.
        """
        try: return self.get(is_preferred=True, **kwargs)
        except self.model.DoesNotExist:
            try: return self.filter(**kwargs)[0]
            except IndexError: return default
            
def create_geo_alt_names(geo_type):
    geo_alt_names = {}
    for locale in settings.locales:
        name_format = geo_type.__name__ + '{}' + locale.capitalize()
        name = name_format.format('AltName')
        geo_alt_names[locale] = create_model(
            name = name,
            fields = {
                'geo': models.ForeignKey(geo_type,                              # Related geo type
                    related_name = 'alt_names_' + locale),                              
                'name': models.CharField(max_length=200, db_index=True),        # Alternate name
                'is_preferred': models.BooleanField(),                          # True if this alternate name is an official / preferred name
                'is_short': models.BooleanField(),                              # True if this is a short name like 'California' for 'State of California'
                'objects': GeoAltNameManager(),
                '__unicode__': lambda self: force_unicode(self.name),
            },
            app_label = 'cities',
            module = 'cities.models',
            options = {
                'db_table': 'cities_' + un_camel(name),
                'verbose_name': un_camel(name).replace('_', ' '),
                'verbose_name_plural': un_camel(name_format.format('AltNames')).replace('_', ' '),
            },
        )
    return geo_alt_names

geo_alt_names = {}
for type in [Country, Region, City, District]:
    geo_alt_names[type] = create_geo_alt_names(type)

    
def create_postal_codes():
    
    @property
    def parent(self):
        """Returns region if available, otherwise country"""
        return self.region if self.region else self.country
        
    @property
    def hierarchy(self):
        """Get hierarchy, root first"""
        list = self.parent.hierarchy
        list.append(self)
        return list
    
    @property
    def names(self):
        """Get a hierarchy of non-null names, root first"""
        return [e for e in [
            force_unicode(self.country),
            force_unicode(self.region_0_name),
            force_unicode(self.region_1_name),
            force_unicode(self.region_2_name),
            force_unicode(self.name),
        ] if e]
        
    @property
    def name_full(self):
        """Get full name including hierarchy"""
        return u', '.join(reversed(self.names))
        
    postal_codes = {}
    for country in settings.postal_codes:
        name_format = "{}" + country
        name = name_format.format('PostalCode')
        postal_codes[country] = create_model(
            name = name,
            fields = {
                'country': models.ForeignKey(Country,
                    related_name = 'postal_codes_' + country),
                'code': models.CharField(max_length=20, db_index=True),
                'name': models.CharField(max_length=200, db_index=True),
                'region_0_name': models.CharField(max_length=100, db_index=True, verbose_name="region 0 name (state)"),
                'region_1_name': models.CharField(max_length=100, db_index=True, verbose_name="region 1 name (county)"),
                'region_2_name': models.CharField(max_length=100, db_index=True, verbose_name="region 2 name (community)"),
                'region': models.ForeignKey(Region, null=True, blank=True,
                    related_name = 'postal_codes_' + country),
                'location': models.PointField(),
                'objects': models.GeoManager(),
                'parent': parent,
                'hierarchy': hierarchy,
                'names': names,
                'name_full': name_full,
                '__unicode__': lambda self: force_unicode(self.code),
            },
            app_label = 'cities',
            module = 'cities.models',
            options = {
                'db_table': 'cities_' + un_camel(name),
                'verbose_name': un_camel(name).replace('_', ' '),
                'verbose_name_plural': un_camel(name_format.format('PostalCodes')).replace('_', ' '),
            },
        )
    return postal_codes

postal_codes = create_postal_codes()


