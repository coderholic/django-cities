from django.conf import settings
from django.utils.encoding import force_unicode
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from util import create_model, un_camel
    
class Country(models.Model):
    name = models.CharField(max_length=200, db_index=True)      # ASCII name
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

    @property
    def hierarchy(self):
        return [self]

class Region(models.Model):
    name = models.CharField(max_length=200, db_index=True)      # ASCII name
    name_std = models.CharField(max_length=200, db_index=True)  # UTF-8 international standard name
    slug = models.CharField(max_length=200)
    code = models.CharField(max_length=10, db_index=True)
    country = models.ForeignKey(Country)
    objects = models.GeoManager()

    def __unicode__(self):
        return u'{}, {}'.format(force_unicode(self.name_std), self.country)

    @property
    def hierarchy(self):
        list = self.country.hierarchy
        list.append(self)
        return list

class City(models.Model):
    name = models.CharField(max_length=200, db_index=True)      # ASCII name
    name_std = models.CharField(max_length=200, db_index=True)  # UTF-8 international standard name
    slug = models.CharField(max_length=200)
    region = models.ForeignKey(Region)
    location = models.PointField()
    population = models.IntegerField()
    objects = models.GeoManager()

    class Meta:
        verbose_name_plural = "cities"
        
    def __unicode__(self):
        return u'{}, {}'.format(force_unicode(self.name_std), self.region)

    @property
    def hierarchy(self):
        list = self.region.hierarchy
        list.append(self)
        return list

class District(models.Model):
    name = models.CharField(max_length=200, db_index=True)      # ASCII name
    name_std = models.CharField(max_length=200, db_index=True)  # UTF-8 international standard name
    slug = models.CharField(max_length=200)
    city = models.ForeignKey(City)
    location = models.PointField()
    population = models.IntegerField()
    objects = models.GeoManager()

    def __unicode__(self):
        return u'{}, {}'.format(force_unicode(self.name_std), self.city)

    @property
    def hierarchy(self):
        list = self.city.hierarchy
        list.append(self)
        return list

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

def _create_geo_alt_name(geo_type):
    geo_alt_names = {}
    for locale in settings.CITIES_LOCALES:
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
    geo_alt_names[type] = _create_geo_alt_name(type)
