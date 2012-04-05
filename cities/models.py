from django.utils.encoding import force_unicode
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from conf import settings
from util import create_model, un_camel
    
__all__ = [
        'Point', 'Country', 'Region', 'Subregion',
        'City', 'District', 'geo_alt_names', 'postal_codes'
]

class Place(models.Model):
    name = models.CharField(max_length=200, db_index=True, verbose_name="ascii name")
    slug = models.CharField(max_length=200)

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
        
class Country(Place):
    code = models.CharField(max_length=2, db_index=True)
    population = models.IntegerField()
    continent = models.CharField(max_length=2)
    tld = models.CharField(max_length=5)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = "countries"

    @property
    def parent(self):
        return None
        
    def __unicode__(self):
        return force_unicode(self.name)

class RegionBase(Place):
    name_std = models.CharField(max_length=200, db_index=True, verbose_name="standard name")
    code = models.CharField(max_length=200, db_index=True)
    country = models.ForeignKey(Country)

    levels = ['region', 'subregion']
    
    class Meta:
        abstract = True
        
    def __unicode__(self):
        return u'{}, {}'.format(force_unicode(self.name_std), self.parent)
        
class Region(RegionBase):
     
    @property
    def parent(self):
        return self.country
        
class Subregion(RegionBase):
    region = models.ForeignKey(Region)
    
    @property
    def parent(self):
        return self.region
        
class CityBase(Place):
    name_std = models.CharField(max_length=200, db_index=True, verbose_name="standard name")
    location = models.PointField()
    population = models.IntegerField()
    
    class Meta:
        abstract = True 
        
    def __unicode__(self):
        return u'{}, {}'.format(force_unicode(self.name_std), self.parent)
        
class City(CityBase):
    region = models.ForeignKey(Region, null=True, blank=True)
    subregion = models.ForeignKey(Subregion, null=True, blank=True)
    country = models.ForeignKey(Country)
    
    class Meta:
        verbose_name_plural = "cities"
        
    @property
    def parent(self):
        for parent_name in reversed(['country'] + RegionBase.levels):
            parent_obj = getattr(self, parent_name)
            if parent_obj: return parent_obj
        return None

class District(CityBase):
    city = models.ForeignKey(City)
    
    @property
    def parent(self):
        return self.city

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
for type in [Country, Region, Subregion, City, District]:
    geo_alt_names[type] = create_geo_alt_names(type)

    
def create_postal_codes():
    
    @property
    def parent(self):
        for parent_name in reversed(['country'] + RegionBase.levels):
            parent_obj = getattr(self, parent_name)
            if parent_obj: return parent_obj
        return None
        
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
            force_unicode(self.region_name),
            force_unicode(self.subregion_name),
            force_unicode(self.district_name),
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
                'code': models.CharField(max_length=20, primary_key=True),
                'name': models.CharField(max_length=200, db_index=True),
                # Region names for each admin level, region may not exist in DB
                'region_name': models.CharField(max_length=100, db_index=True),
                'subregion_name': models.CharField(max_length=100, db_index=True),
                'district_name': models.CharField(max_length=100, db_index=True),
                'region': models.ForeignKey(Region, null=True, blank=True, related_name = 'postal_codes_' + country),
                'subregion': models.ForeignKey(Subregion, null=True, blank=True, related_name = 'postal_codes_' + country),
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


