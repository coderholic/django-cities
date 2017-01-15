# django-cities

## Place models and worldwide place data for Django

[![PyPI version](https://badge.fury.io/py/django-cities.svg)](https://badge.fury.io/py/django-cities) [![Build status](https://travis-ci.org/coderholic/django-cities.svg?branch=master)](https://travis-ci.org/coderholic/django-cities.svg?branch=master)

----

django-cities provides you with place related models (eg. Country, Region, City) and data (from [GeoNames](http://www.geonames.org/)) that can be used in your django projects.

This package officially supports all currently supported versions of Python/Django:

|      Python   | 2.7 | 3.3 | 3.4 | 3.5 | 3.6 |
| :------------ | --- | --- | --- | --- | --- |
| Django 1.7    |  :white_square_button:  |  :white_square_button:  |  :white_square_button:  | :x: | :x: |
| Django 1.8    |  :white_check_mark:  |  :white_check_mark:  |  :white_check_mark:  |  :white_check_mark:  | :large_blue_circle: |
| Django 1.9    |  :white_check_mark:  | :x: |  :white_check_mark:  |  :white_check_mark:  | :large_blue_circle: |
| Django 1.10   |  :white_check_mark:  | :x: |  :white_check_mark:  |  :white_check_mark:  | :large_blue_circle: |
| Django [master](https://github.com/django/django/archive/master.tar.gz) | :large_blue_circle: | :x: | :large_blue_circle: | :large_blue_circle: | :large_blue_circle: |

| Key |                                                                     |
| :-: | :------------------------------------------------------------------ |
| :white_check_mark: | Officially supported, tested, and passing                           |
| :large_blue_circle: | Tested and passing, but not officially supported                    |
| :white_square_button: | Not officially supported, may break at any time, most tests passing |
| :x: | Known incompatibilities                                             |

Authored by [Ben Dowling](http://www.coderholic.com), and some great [contributors](https://github.com/coderholic/django-cities/contributors).

See some of the data in action at [city.io](http://city.io) and [country.io](http://country.io).

----

## Requirements

Your database must support spatial queries, see the [GeoDjango documentation](https://docs.djangoproject.com/en/dev/ref/contrib/gis/) for details and setup instructions.



## Installation

Clone this repository into your project:

```bash
git clone https://github.com/coderholic/django-cities.git
```

Download the zip file and unpack it:

```bash
wget https://github.com/coderholic/django-cities/archive/master.zip
unzip master.zip
```

Install with pip:

```bash
pip install django-cities
```



## Configuration

You'll need to add `cities` to `INSTALLED_APPS` in your projects `settings.py` file:

```python
INSTALLED_APPS = (
    # ...
    'cities',
    # ...
)
```

### Migration Configuration

These settings should be reviewed and set or modified before any migrations have been committed.

#### Swappable Models

This project supports swappable models using the [django-swappable-models project](https://github.com/wq/django-swappable-models).

|   Model   |       Setting Name       |    Default Value   |
| :-------- | :----------------------- | :----------------- |
| Continent | `CITIES_CONTINENT_MODEL` | `cities.Continent` |
| Country   | `CITIES_COUNTRY_MODEL`   | `cities.Country`   |
| City      | `CITIES_CITY_MODEL`      | `cities.City`      |

#### Alternative Name Types

The Geonames data for alternative names contain additional information, such as links to external websites (mostly Wikipedia articles) and pronunciation guides (pinyin). However, django-cities only uses and imports a subset of those types. Since some users may wish to use them all, the `CITIES_ALTERNATIVE_NAME_TYPES` and `CITIES_AIRPORT_TYPES` settings can be used to define the alternative name types in the database.

These settings should be specified as a tuple of tuple choices:

```python
CITIES_AIRPORT_TYPES = (
    ('iata', _("IATA (Airport) Code")),
    ('icao', _("ICAO (Airport) Code")),
    ('faac', _("FAAC (Airport) Code")),
)

CITIES_ALTERNATIVE_NAME_TYPES = (
    ('name', _("Name")),
    ('abbr', _("Abbreviation")),
    ('link', _("Link")),
)
```

If `CITIES_INCLUDE_AIRPORT_CODES` is set to `True`, the choices in `CITIES_AIRPORT_TYPES` will be appended to the `CITIES_ALTERNATIVE_NAME_TYPES` choices. Otherwise, no airport types are imported.

The Geonames data also contains alternative names that are purely numeric

The `CITIES_INCLUDE_NUMERIC_ALTERNATIVE_NAMES` setting controls whether or not purely numeric alternative names are imported. 

#### Continent Data

Since continent data rarely (if ever) changes, the continent data is loaded directly from Python data structures included with the django-cities distribution. However, there are different continent models with different numbers of continents. Therefore, some users may wish to override the default settings by setting the `CITIES_CONTINENT_DATA` to a Python dictionary where the keys are the continent code and the values are (name, id) tuples.

The following is the default continent data in [`cities/conf.py`](https://github.com/coderholic/django-cities/blob/master/cities/conf.py#L178):

```python
CITIES_CONTINENT_DATA = {
    'AF': ('Africa', 6255146),
    'AS': ('Asia', 6255147),
    'EU': ('Europe', 6255148),
    'NA': ('North America', 6255149),
    'OC': ('Oceania', 6255151),
    'SA': ('South America', 6255150),
    'AN': ('Antarctica', 6255152),
}
```

### Run Migrations

After you have configured all migration settings, run

```bash
python manage.py migrate cities
```

to create the required database tables.



### Import Configuration

These settings should also be reviewed and set or modified before importing any data. Changing these settings after importing data may not have the intended effect.

#### Download Directory

Specify a download directory (used to specify a writable directory).

Default: `cities/data`

You may want to use this if you are on a cloud services provider, or if django-cities is installed on a read-only medium.

Note that this path must be an absolute path.

```python
CITIES_DATA_DIR = '/var/data'
```

#### Download Files

You can override the files the import command uses to process data:

```python
CITIES_FILES = {
    # ...
    'city': {
       'filename': 'cities1000.zip',
       'urls':     ['http://download.geonames.org/export/dump/'+'{filename}']
    },
    # ...
}
```

It is also possible to specify multiple filenames to process. Note that these files are processed in the order they are specified, so duplicate data in files specified later in the list will overwrite data from files specified earlier in the list.

```python
CITIES_FILES = {
    # ...
    'city': {
       'filenames': ["US.zip", "GB.zip", ],
       'urls':     ['http://download.geonames.org/export/dump/'+'{filename}']
    },
    # ...
}
```

#### Currency Data

The Geonames data includes currency data, but it is limited to the currency code (example: "USD") and the currency name (example: "Dollar"). The django-cities package offers the ability to import currency symbols (example: "$") with the country model.

However, like the continent data, since this rarely changes, the currency symbols is loaded directly from Python data structures included with the django-cities distribution in the `CITIES_CURRENCY_SYMBOLS` setting. Users can override this setting if they wish to add or modify the imported currency symbols.

For default values see the included [`cities/conf.py` file](https://github.com/coderholic/django-cities/blob/master/cities/conf.py#L189).

```python
CITIES_CURRENCY_SYMBOLS = {
    "AED": "د.إ", "AFN": "؋", "ALL": "L", "AMD": "դր.", "ANG": "ƒ", "AOA": "Kz",
    "ARS": "$", "AUD": "$", "AWG": "ƒ", "AZN": "m",
    "BAM": "KM", "BBD": "$", "BDT": "৳", "BGN": "лв", "BHD": "ب.د", "BIF": "Fr",
    # ...
    "UAH": "₴", "UGX": "Sh", "USD": "$", "UYU": "$", "UZS": "лв",
```

#### Countries That No Longer Exist

The Geonames data includes countries that no longer exist. At this time, those countries are the Dutch Antilles (`AN`) and Serbia and Montenegro (`CS`). If you wish to import those countries, set the `CITIES_NO_LONGER_EXISTENT_COUNTRY_CODES` to an empty list (`[]`).

Default: `['CS', 'AN']`

```python
CITIES_NO_LONGER_EXISTENT_COUNTRY_CODES = ['CS', 'AN']
```

#### Postal Code Validation

The Geonames data contains country postal code formats and regular expressions, as well as postal codes. Some of these postal codes do not match the regular expression of their country. Users who wish to ignore these postal codes when importing data can set the `CITIES_VALIDATE_POSTAL_CODES` setting to `True` to skip importing postal codes that do not validate the country postal code regular expression.

If you have regional knowledge of postal codes that do not validate, please either update the postal code itself or the country postal codes regular expression on the Geonames website. Doing this will help all Geonames users (including this project but also every other Geonames user).

```python
CITIES_VALIDATE_POSTAL_CODES = True
```

#### Custom `slugify()` Function

You may wish to customize the slugs generated by django-cities. To do so, you will need to write your own `slugify()` function and specify its dotted import path in the `CITIES_SLUGIFY_FUNCTION`:

```python
CITIES_SLUGIFY_FUNCTION = 'cities.util.default_slugify'
```

Your customized slugify function should accept two arguments: the object itself and the slug generated by the object itself. It should return the final slug as a string.

Because the slugify function contains code that would be reused by multiple objects, there is only a single slugify function for all of the objects in django-cities. To generate different slugs for different types of objects, test against the object's class name (`obj.__class__.__name__`).

Default slugify function (see [`cities/util.py`](https://github.com/coderholic/django-cities/tree/master/cities/util.py#L35)):

```python
# SLUGIFY REGEXES

to_und_rgx = re.compile(r"[']", re.UNICODE)
slugify_rgx = re.compile(r'[^-\w._~]', re.UNICODE)
multi_dash_rgx = re.compile(r'-{2,}', re.UNICODE)
dash_und_rgx = re.compile(r'[-_]_', re.UNICODE)
und_dash_rgx = re.compile(r'[-_]-', re.UNICODE)
starting_chars_rgx = re.compile(r'^[-._]*', re.UNICODE)
ending_chars_rgx = re.compile(r'[-._]*$', re.UNICODE)


def default_slugify(obj, value):
    if value is None:
        return None

    value = force_text(unicode_func(value))
    value = unicodedata.normalize('NFKC', value.strip())
    value = re.sub(to_und_rgx, '_', value)
    value = re.sub(slugify_rgx, '-', value)
    value = re.sub(multi_dash_rgx, '-', value)
    value = re.sub(dash_und_rgx, '_', value)
    value = re.sub(und_dash_rgx, '_', value)
    value = re.sub(starting_chars_rgx, '', value)
    value = re.sub(ending_chars_rgx, '', value)
    return mark_safe(value)
```

#### Cities Without Regions

Some cities in the Geonames data files do not have region information. By default, these cities are imported as normal (they still have foreign keys to their country), but if you wish to *avoid* importing these cities, set `CITIES_IGNORE_EMPTY_REGIONS` to `True`:

```python
# Import cities without region (default False)
CITIES_IGNORE_EMPTY_REGIONS = True
```

#### Languages/Locales To Import

Limit imported alternative names by languages/locales

Note that many alternative names in the Geonames data do not specify a language code, so if you manually specify language codes and do not include `und`, you may not import as many alternative names as you want.

Special values:

* `ALL` - import all alternative names
* `und` - alternative names that do not specify a language code. When imported, these alternative names will be assigned a language code of `und`. If this language code is not specified, alternative names that do not specify a language code are not imported.
* `LANGUAGES` - a "shortcut" to import all alternative names specified in the `LANGUAGES` setting in your Django project's `settings.py`

For a full list of ISO639-1 language codes, see the [iso-languagecodes.txt](http://download.geonames.org/export/dump/iso-languagecodes.txt) file on Geonames.

```python
CITIES_LOCALES = ['en', 'und', 'LANGUAGES']
```

#### Limit Imported Postal Codes

Limit the imported postal codes to specific countries

Special value:

* `ALL` - import all postal codes

```python
CITIES_POSTAL_CODES = ['US', 'CA']
```

#### Plugins

You can write your own plugins (see the [#Writing plugins](#writing-plugins) section) to process data before and after it is written to the database. This is how you would activate them:

```python
CITIES_PLUGINS = [
    # Canadian postal codes need region codes remapped to match geonames
    'cities.plugin.postal_code_ca.Plugin',
    # Reduce memory usage when importing large datasets (e.g. "allCountries.zip")
    'cities.plugin.reset_queries.Plugin',
]
```

Note that some plugins may use their own configuration options:

```python
# This setting may be specified if you use 'cities.plugin.reset_queries.Plugin'
CITIES_PLUGINS_RESET_QUERIES_CHANCE = 1.0 / 1000000
```

### Import Data

After you have configured all import settings, run

```bash
python manage.py cities --import=all
```

to import all of the place data.

You may also import specific object types:

```bash
python manage.py cities --import=country
```

```bash
python manage.py cities --import=city
```

**NOTE:** This can take a long time, although there are progress bars drawn in the terminal.

Specifically, importing postal codes can take one or two orders of magnitude more time than importing other objects.



### Writing Plugins

You can specify the import path of any class in `CITIES_PLUGINS` (see the `CITIES_PLUGINS` section in the [configuration section](#configuration)).

Here is a complete skeleton plugin class example; note that only one of these methods is required:

```python
class CompleteSkeletonPlugin(object):
    """
    Skeleton plugin for django-cities that has hooks for all object types, and
    does not modify any import data or existing objects in the database.
    """
    # Note: Only ONE of these methods needs to be defined. If a method is not
    #       defined, the import command will avoid calling the undefined method.

    def country_pre(self, parser, imported_data_dict):
        pass

    def country_post(self, parser, country_instance, imported_data_dict):
        pass

    def region_pre(self, parser, imported_data_dict):
        pass

    def region_post(self, parser, region_instance, imported_data_dict):
        pass

    def subregion_pre(self, parser, imported_data_dict):
        pass

    def subregion_post(self, parser, subregion_instance, imported_data_dict):
        pass

    def city_pre(self, parser, imported_data_dict):
        pass

    def city_post(self, parser, city_instance, imported_data_dict):
        pass

    def district_pre(self, parser, imported_data_dict):
        pass

    def district_post(self, parser, district_instance, imported_data_dict):
        pass

    def alt_name_pre(self, parser, imported_data_dict):
        pass

    def alt_name_post(self, parser, alt_name_instance, imported_data_dict):
        pass

    def postal_code_pre(self, parser, imported_data_dict):
        pass

    def postal_code_post(self, parser, postal_code_instance, imported_data_dict):
        pass
```

Arguments passed to hooks:

* `self` - the plugin object itself
* `parser` - the instance of the "cities.Command" management command
* `<model>_instance` - instance of model that was created based on `item`
* `imported_data_dict`- dict instance with data for row being processed

Silly example:

```python
class DorothyPlugin(object):
    def city_pre(self, parser, import_dict):
        # Skip importing cities not in Kansas
        if import_dict['cc2'] == 'US' and import_dict['admin1Code'] != 'KS':
            return False  # Returning a False-y value skips importing the item
        else:
            # Modify the value of the data before it is written to the database
            import_dict['admin1Code'] = 'KS'

    def city_post(self, parser, city, import_data):
        # Checks if the region foreign key for the city database row is NULL
        if city.region is None:
            # Sets it to Kansas
            city.region = Region.objects.get(country__code='US', code='KS')
            # Re-save any existing items that aren't in Kansas
            city.save()
            # There's no place like home
```



### Examples

This repository contains an example project which lets you browse the place hierarchy. See the [`example directory`](https://github.com/coderholic/django-cities/tree/master/example). Below are some small snippets to show you the kind of queries that are possible once you have imported data:


```python
# Find the 5 most populated countries in the World
>>> Country.objects.order_by('-population')[:5]
[<Country: China>, <Country: India>, <Country: United States>,
 <Country: Indonesia>, <Country: Brazil>]

# Find what country the .ly TLD belongs to
>>> Country.objects.get(tld='ly')
<Country: Libya>

# 5 Nearest cities to London
>>> london = City.objects.filter(country__name='United Kingdom').get(name='London')
>>> nearest = City.objects.distance(london.location).exclude(id=london.id).order_by('distance')[:5]

# All cities in a state or county
>>> City.objects.filter(country__code="US", region__code="TX")
>>> City.objects.filter(country__name="United States", subregion__name="Orange County")

# Get all countries in Japanese preferring official names if available,
# fallback on ASCII names:
>>> [country.alt_names_ja.get_preferred(default=country.name) for country in Country.objects.all()]

# Alternate names for the US in English, Spanish and German
>>> [x.name for x in Country.objects.get(code='US').alt_names.filter(language_code='de')]
[u'USA', u'Vereinigte Staaten']
>>> [x.name for x in Country.objects.get(code='US').alt_names.filter(language_code='es')]
[u'Estados Unidos']
>>> [x.name for x in Country.objects.get(code='US').alt_names.filter(language_code='en')]
[u'United States of America', u'America', u'United States']

# Alternative names for Vancouver, Canada
>>> City.objects.get(name='Vancouver', country__code='CA').alt_names.all()
[<AlternativeName: 溫哥華 (yue)>, <AlternativeName: Vankuver (uz)>,
 <AlternativeName: Ванкувер (ce)>, <AlternativeName: 溫哥華 (zh)>,
 <AlternativeName: वैंकूवर (hi)>, <AlternativeName: Ванкувер (tt)>,
 <AlternativeName: Vankuveris (lt)>, <AlternativeName: Fankoever (fy)>,
 <AlternativeName: فانكوفر (arz)>, <AlternativeName: Ванкувер (mn)>,
 <AlternativeName: ဗန်ကူးဗားမ_ (my)>, <AlternativeName: व्हँकूव्हर (mr)>,
 <AlternternativeName: வான்கூவர் (ta)>, <AlternativeName: فانكوفر (ar)>,
 <AlternativeName: Vankuver (az)>, <AlternativeName: Горад Ванкувер (be)>,
 <AlternativeName: ভ্যানকুভার (bn)>, <AlternativeName: แวนคูเวอร์ (th)>,
 <Al <AlternativeName: Ванкувер (uk)>, <AlternativeName: ਵੈਨਕੂਵਰ (pa)>,
 '...(remaining elements truncated)...']

# Get zip codes near Mountain View, CA
>>> PostalCode.objects.distance(City.objects.get(name='Mountain View', region__name='California').location).order_by('distance')[:5]
[<PostalCode: 94040>, <PostalCode: 94041>, <PostalCode: 94043>,
 <PostalCode: 94024>, <PostalCode: 94022>]
```



###  Third-party Apps / Extensions

These are apps that build on top of the `django-cities`. Useful for essentially extending what `django-cities` can do.

* [django-airports](https://github.com/bashu/django-airports) provides you with airport related model and data (from OpenFlights) that can be used in your Django projects.



### TODO

* Integrate [libpostal](https://github.com/openvenues/libpostal) to extract Country/City/District/Postal Code from an address string
* Add tests for importing districts
* Add contrib module for Django REST framework, similar to django-contrib-light's [`restframework3`](https://github.com/yourlabs/django-cities-light/blob/stable/3.x.x/cities_light/contrib/restframework3.py)
* Add autocomplete with [`django-autocomplete-light`](https://github.com/yourlabs/django-autocomplete-light)
* Minimize number of attributes on base models



### Notes

Some datasets are very large (> 100 MB) and take time to download/import.

Data will only be downloaded/imported if it is newer than your data, and only matching rows will be overwritten.

The cities manage command has options, see `--help`.  Verbosity is controlled through the `LOGGING` setting.



## Running Tests

1. Install postgres, postgis and libgdal-dev
2. Create `django_cities` database:

        sudo su -l postgres
        # Enter your password
        createuser -d -s -P some_username
        # Enter password
        createdb -T template0 -E utf-8 -l en_US.UTF-8 -O multitest django_cities
        psql  -c 'create extension postgis;' -d django_cities

3. Run tests:

        POSTGRES_USER=some_username POSTGRES_PASSWORD='password from createuser step' tox

        # If you have changed example data files then you should push your
        # changes to github and specify commit and repo variables:
        TRAVIS_COMMIT=`git rev-parse HEAD` TRAVIS_REPO_SLUG='github-username/django-cities' POSTGRES_USER=some_username POSTGRES_PASSWORD='password from createuser ste' tox

#### Useful test options:

* `TRAVIS_LOG_LEVEL` - defaults to `INFO`, but set to `DEBUG` to see a (very) large and (very) complete log of the import script
* `CITIES_FILES` - set the base urls to a `file://` path to use local files without modifying any other settings


## Release Notes

### 0.4.1

Use Django's native migrations

#### Upgrading from 0.4.1

Upgrading from 0.4.1 is likely to cause problems trying to apply a migration when the tables already exist. In this case a fake migration needs to be applied:

```bash
python manage.py migrate cities 0001 --fake
```

### 0.4

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
