# django-cities
### Place models and worldwide place data for Django

----

django-cities provides you with place related models (eg. Country, Region, City) and data (from [GeoNames](http://www.geonames.org/)) that can be used in your django projects.

Authored by [Ben Dowling](http://www.coderholic.com), and some great [contributors](https://github.com/coderholic/django-cities/contributors).

----

### 0.4 Release notes

** **This release of django-cities is not backwards compatible with previous versions** **

The country model has some new fields:
 - elevation
 - area
 - currency
 - currency_name
 - languages
 - neighbours
 - capital
 - phone

Alternative name support has been completely overhauled. The code and usage should now be much simpler. See the updated examples below.

The code field no longer contains the parent code. Eg. the code for California, US is now "CA". In the previous release it was "US.CA".

These changes mean that upgrading from a previous version isn't simple. All of the place IDs are the same though, so if you do want to upgrade it should be possible.

### Requirements

Your database must support spatial queries, see the [GeoDjango documentation](https://docs.djangoproject.com/en/dev/ref/contrib/gis/) for details and setup instructions.


### Setup

Either clone this repository into your project, or install with ```pip install django-cities```

You'll need to add ```cities``` to ```INSTALLED_APPS``` in your projects settings.py file:

```python
import django

INSTALLED_APPS = (
    ...
    'cities',
)

if django.VERSION < (1, 7):
    INSTALLED_APPS += (
        'south',
    )
```

Then run ```./manage.py syncdb``` to create the required database tables, and ```./manage.py cities --import=all``` to import all of the place data. **NOTE:** This can take a long time.

#### Upgrading from 0.4.1

Upgrading from 0.4.1 is likely to cause problems trying to apply a
migration when the tables already exist. In this case a fake migration
needs to be applied:

```shell
./manage.py migrate cities 0001 --fake
```

### Configuration

There are various optional configuration options you can set in your ```settings.py```:

```python
# Override the default source files and URLs
CITIES_FILES = {
    'city': {
       'filename': 'cities1000.zip',
       'urls':     ['http://download.geonames.org/export/dump/'+'{filename}']
    },
}

# Alternatively you can specify multiple filenames to process:
CITIES_FILES = {
    'city': {
       'filenames': ["US.zip", "GB.zip", ],
       'urls':     ['http://download.geonames.org/export/dump/'+'{filename}']
    },
}

# Localized names will be imported for all ISO 639-1 locale codes below.
# 'und' is undetermined language data (most alternate names are missing a lang tag).
# See download.geonames.org/export/dump/iso-languagecodes.txt
# 'LANGUAGES' will match your language settings, and 'ALL' will install everything
CITIES_LOCALES = ['en', 'und', 'LANGUAGES']

# full path of folder where the data from geonames.org are downloaded
# by default all data are downloaded in folder 'data' relative to package installation
CITIES_DATA_DIR = '/var/data'

# Postal codes will be imported for all ISO 3166-1 alpha-2 country codes below.
# You can also specificy 'ALL' to import all postal codes.
# See cities.conf for a full list of country codes. 'ALL' will install everything.
# See download.geonames.org/export/dump/countryInfo.txt
CITIES_POSTAL_CODES = ['US', 'CA']

# List of plugins to process data during import
CITIES_PLUGINS = [
    'cities.plugin.postal_code_ca.Plugin',  # Canada postal codes need region codes remapped to match geonames
    'cities.plugin.reset_queries.Plugin',  # plugin that helps to reduce memory usage when importing large datasets (e.g. "allCountries.zip")
]

# Import cities without region (default False)
CITIES_IGNORE_EMPTY_REGIONS = True

# This setting may be specified if you use 'cities.plugin.reset_queries.Plugin'
CITIES_PLUGINS_RESET_QUERIES_CHANCE = 1.0 / 1000000
```


### Writing plugins

You can specify import path of any class in ``CITIES_PLUGINS``. to affect import it should have one of following methods:

* ``FOO_pre(self, parser, item)``;
* ``FOO_post(self, parser, model_instance, item)``,

where "FOO" should be one of: "country", "region", "subregion", "city", "district", "alt_name" or "postal_code".

Arguments passed to hooks:

* ``parser``: instance of "cities" management command;
* ``item``: dict instance with data for row being processed;
* ``model_instance``: instance of model that was created based on ``item``.

### Examples

This repository contains an example project which lets you browse the place hierarchy. See the ```example``` directory. Below are some small snippets to show you the kind of things that are possible:


```python
# Find the 5 most populated countries in the World
>>> Country.objects.order_by('-population')[:5]
[<Country: China>, <Country: India>, <Country: United States>, <Country: Indonesia>, <Country: Brazil>]

# Find what country the .ly TLD belongs to
>>> Country.objects.get(tld='ly')
<Country: Libya>

# 5 Nearest cities to London
>>> london = City.objects.filter(country__name='United Kingdom').get(name='London')
>>> nearest = City.objects.distance(london.location).exclude(id=london.id).order_by('distance')[:5]

# All cities in a state or county
>>> City.objects.filter(country__code="US", region__code="TX")
>>> City.objects.filter(country__name="United States", subregion__name="Orange County")

# Get all countries in Japanese preferring official names if available, fallback on ASCII names:
>>> [country.alt_names_ja.get_preferred(default=country.name) for country in Country.objects.all()]

# Alternate names for the US in English, Spanish and German
>>> [x.name for x in Country.objects.get(code='US').alt_names.filter(language='de')]
[u'USA', u'Vereinigte Staaten']
>>> [x.name for x in Country.objects.get(code='US').alt_names.filter(language='es')]
[u'Estados Unidos']
>>> [x.name for x in Country.objects.get(code='US').alt_names.filter(language='en')]
[u'United States of America', u'America', u'United States']

# Alternative names for Vancouver, Canada
>>> City.objects.get(name='Vancouver', country__code='CA').alt_names.all()
[<AlternativeName: 溫哥華 (yue)>, <AlternativeName: Vankuver (uz)>, <AlternativeName: Ванкувер (ce)>, <AlternativeName: 溫哥華 (zh)>, <AlternativeName: वैंकूवर (hi)>, <AlternativeName: Ванкувер (tt)>, <AlternativeName: Vankuveris (lt)>, <AlternativeName: Fankoever (fy)>, <AlternativeName: فانكوفر (arz)>, <AlternativeName: Ванкувер (mn)>, <AlternativeName: ဗန်ကူးဗားမ_ (my)>, <AlternativeName: व्हँकूव्हर (mr)>, <AlternternativeName: வான்கூவர் (ta)>, <AlternativeName: فانكوفر (ar)>, <AlternativeName: Vankuver (az)>, <AlternativeName: Горад Ванкувер (be)>, <AlternativeName: ভ্যানকুভার (bn)>, <AlternativeName: แวนคูเวอร์ (th)>, <Al <AlternativeName: Ванкувер (uk)>, <AlternativeName: ਵੈਨਕੂਵਰ (pa)>, '...(remaining elements truncated)...']

# Get zip codes near Mountain View, CA
>>> PostalCode.objects.distance(City.objects.get(name='Mountain View', region__name='California').location).order_by('distance')[:5]
[<PostalCode: 94040>, <PostalCode: 94041>, <PostalCode: 94043>, <PostalCode: 94024>, <PostalCode: 94022>]
```

###  Third-party apps / extensions

These are apps that build on top of the ``django-cities``. Useful for essentially extending what ``django-cities`` can do.

* [django-airports](https://github.com/bashu/django-airports) provides you with airport related model and data (from OpenFlights) that can be used in your django projects.

### Running tests

1. install postgres, postgis and libgdal-dev
2. create django_cities database:

        sudo su -l postgres
        # Enter your password
        createuser -d -s -P some_username
        # Enter password
        createdb -T template0 -E utf-8 -l en_US.UTF-8 -O multitest django_cities
        psql  -c 'create extension postgis;' -d django_cities

3. Run tests:

        POSTGRES_USER=some_username POSTGRES_PASSWORD='password from createuser step' tox

        # if you have changed example data files then you should push your changes to github and specify commit and repo variables:
        TRAVIS_COMMIT=`git rev-parse HEAD` TRAVIS_REPO_SLUG='github-username/django-cities' POSTGRES_USER=some_username POSTGRES_PASSWORD='password from createuser ste' tox


### Notes

Some datasets are very large (> 100 MB) and take time to download / import.

Data will only be downloaded / imported if it is newer than your data, and only matching rows will be overwritten.

The cities manage command has options, see --help.  Verbosity is controlled through LOGGING.
