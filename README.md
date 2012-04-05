 django-cities -- *Place models and data for Django apps*
=========================================================

This add-on provides models and commands to import country/region/city data into your database.
The data is pulled from [GeoNames](http://www.geonames.org/) and contains:

  - localized names
  - geographical codes
  - postal codes
  - geo-coords
  - population

Your database must support spatial queries, see [GeoDjango]
(https://docs.djangoproject.com/en/dev/ref/contrib/gis/) for setup.

For more information see [this blog post]
(http://www.coderholic.com/django-cities-countries-regions-cities-and-districts-for-django/).


 Examples
--------------------------
Finding all London boroughs:

```python
    london = City.objects.filter(country__name='United Kingdom').get(name='London')
    boroughs = District.objects.filter(city=london)
```

Nearest city to a given geo-coord (longitude, latitude):

```python
    City.objects.distance(Point(1, 51)).order_by('distance')[0]
    <City: Dymchurch, Kent, United Kingdom>
```

5 Nearest cities to London:

```python
    london = City.objects.filter(country__name='United Kingdom').get(name='London')
    nearest = City.objects.distance(london.location).exclude(id=london.id).order_by('distance')[:5]
```

Get a list of all cities in a state or county:

```python
    City.objects.filter(country__name="United States", region__name="Texas")
    City.objects.filter(country__name="United States", subregion__name="Orange County")
```

Get all countries in Japanese preferring official names if available, fallback on ASCII names:

```python
    [country.alt_names_ja.get_preferred(default=country.name) for country in Country.objects.all()]
```

Use alternate names model to get Vancouver in Japanese:

```python
    geo_alt_names[City]['ja'].objects.get_preferred(geo__name='Vancouver', default='Vancouver')
```

Gather names of Tokyo from all CITIES_LOCALES:

```python
    [name for locale in cities.conf.settings.locales
        for name in geo_alt_names[City][locale].objects.filter(geo__name='Tokyo')]
```

Get all postal codes for Ontario, Canada (only first 3 letters available due to copyright restrictions):

```python
    postal_codes['CA'].objects.filter(region__name='Ontario')
```

Get region objects for US postal code:

```python
    Region.objects.filter(postal_codes_US__code='90210')
    [<Region: California, United States>]
    Subregion.objects.filter(postal_codes_US__code='90210')
    [<Subregion: Los Angeles County, California, United States>]
```

 Install
--------------------------
- Run: `python setup.py install`
- Add/Merge the following into your *settings.py*:

-----------------------------------------------------------
```python
INSTALLED_APPS = (
    'cities',
)

LOGGING = {
    'handlers': {
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
        },
    },
    'loggers': {
        'cities': {
            'handlers': ['console'],
            'level': 'INFO',
        }
    }
}

CITIES_FILES = {
    # Uncomment below to import all cities with population > 1000 (default is > 5000)
    #'city': {
    #   'filename': 'cities1000.zip',
    #   'urls':     ['http://download.geonames.org/export/dump/'+'{filename}']
    #},
}

# Localized names will be imported for all ISO 639-1 locale codes below.
# 'und' is undetermined language data (most alternate names are missing a lang tag).
# Ref: download.geonames.org/export/dump/iso-languagecodes.txt
CITIES_LOCALES = ['en', 'und']  # + ['LANGUAGES']   # Uncomment to also include languages from your settings

# Postal codes will be imported for all ISO 3166-1 alpha-2 country codes below.
# See cities.conf for a full list of country codes.
# Ref: download.geonames.org/export/dump/countryInfo.txt
CITIES_POSTAL_CODES = ['US', 'CA']

# List of plugins to process data during import
CITIES_PLUGINS = [
    'cities.plugin.postal_code_ca.Plugin',  # Canada postal codes need region codes remapped to match geonames
]
```
-----------------------------------------------------------

- Sync your database with the new models: `manage.py syncdb`
- Populate or update your database: `manage.py cities`


 Notes
--------------------------
The localized names and postal code models/db-tables are created dynamically based on your settings.
Some datasets are very large (> 100 MB) and take time to download / import, and there's no progress display.
Data will only be downloaded / imported if it is newer than your data, and only matching rows will be overwritten.
The cities manage command has options, see --help.  Verbosity is controlled through LOGGING.
