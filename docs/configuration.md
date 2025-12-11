# Configuration

You'll need to enable GeoDjango. See that [documentation](https://docs.djangoproject.com/en/stable/ref/contrib/gis/tutorial/#setting-up) for guidance.

You'll need to add `cities` to `INSTALLED_APPS` in your projects `settings.py` file:

```python
INSTALLED_APPS = (
    # ...
    'cities',
    # ...
)
```

## Migration Configuration

These settings should be reviewed and set or modified BEFORE any migrations have been run.

### Swappable Models

Some users may wish to override some of the default models to add data, override default model methods, or add custom managers. This project supports swapping models out using the [django-swappable-models project](https://github.com/wq/django-swappable-models).

To swap models out, first define your own custom model in your custom cities app. You will need to subclass the appropriate base model from `cities.models`:

Here's an example `my_cities_app/models.py`:

```python
from django.db import models

from cities.models import BaseCountry


class CustomCountryModel(BaseCountry, models.Model):
    more_data = models.TextField()

    class Meta(BaseCountry.Meta):
        pass
```

Then you will need to configure your project by setting the appropriate option:

|   Model   |       Setting Name       |    Default Value   |
| :-------- | :----------------------- | :----------------- |
| Continent | `CITIES_CONTINENT_MODEL` | `cities.Continent` |
| Country   | `CITIES_COUNTRY_MODEL`   | `cities.Country`   |
| City      | `CITIES_CITY_MODEL`      | `cities.City`      |

So to use the `CustomCountryModel` we defined above, we would add the dotted **model** string to our project's `settings.py`:

```python
# ...

CITIES_COUNTRY_MODEL = 'my_cities_app.CustomCountryModel'

# ...
```

The dotted model string is simply the dotted import path with the `.models` substring removed, just `<app_label>.<model_class_name>`.

Once you have set the option in your `settings.py`, all appropriate foreign keys in django-cities will point to your custom model. So in the above example, the foreign keys `Region.country`, `City.country`, and `PostalCode.country` will all automatically point to the `CustomCountryModel`. This means that you do NOT need to customize any dependent models if you don't want to.

### Alternative Name Types

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

The Geonames data also contains alternative names that are purely numeric.

The `CITIES_INCLUDE_NUMERIC_ALTERNATIVE_NAMES` setting controls whether or not purely numeric alternative names are imported. Set to `True` to import them, and to `False` to skip them.

### Continent Data

Since continent data rarely (if ever) changes, the continent data is loaded directly from Python data structures included with the django-cities distribution. However, there are different continent models with different numbers of continents. Therefore, some users may wish to override the default settings by setting the `CITIES_CONTINENT_DATA` to a Python dictionary where the keys are the continent code and the values are (name, geonameid) tuples.

For an overview of different continent models, please see the Wikipedia article on Continents:

https://en.wikipedia.org/wiki/Continent#Number

The following is the default continent data in [`cities/conf.py`](https://github.com/arthanson/django-cities-xtd/blob/master/cities/conf.py#L178):

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

Note that if you do not use these default settings, you will need to register a plugin with a `country_pre` method to adjust the continent ID for country models before countries are processed and saved to the database by the import script. Please contribute your plugin back upstream to this project so that others may benefit from your work by creating a pull request containing your plugin and any relevant documentation for it.

## Run Migrations

After you have configured all migration settings, run

```bash
python manage.py migrate cities
```

to create the required database tables and add the continent data to its table.



## Import Configuration

These settings should also be reviewed and set or modified before importing any data. Changing these settings after importing data may not have the intended effect.

### Download Directory

Specify a download directory (used to specify a writable directory).

Default: `cities/data`

You may want to use this if you are on a cloud services provider, or if django-cities is installed on a read-only medium.

Note that this path must be an absolute path.

```python
CITIES_DATA_DIR = '/var/data'
```

### Download Files

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
       'urls':      ['http://download.geonames.org/export/dump/'+'{filename}']
    },
    # ...
}
```

Note that you do not need to specify all keys in the `CITIES_FILES` dictionary. Any keys you do not specify will use their default values as defined in [`cities/conf.py`](https://github.com/arthanson/django-cities-xtd/blob/master/cities/conf.py#L26).

### Currency Data

The Geonames data includes currency data, but it is limited to the currency code (example: "USD") and the currency name (example: "Dollar"). The django-cities package offers the ability to import currency symbols (example: "$") with the country model.

However, like the continent data, since this rarely changes, the currency symbols are loaded directly from Python data structures included with the django-cities distribution in the `CITIES_CURRENCY_SYMBOLS` setting. Users can override this setting if they wish to add or modify the imported currency symbols.

For default values see the included [`cities/conf.py` file](https://github.com/arthanson/django-cities-xtd/blob/master/cities/conf.py#L189).

```python
CITIES_CURRENCY_SYMBOLS = {
    "AED": "د.إ", "AFN": "؋", "ALL": "L", "AMD": "դր.", "ANG": "ƒ", "AOA": "Kz",
    "ARS": "$", "AUD": "$", "AWG": "ƒ", "AZN": "m",
    "BAM": "KM", "BBD": "$", "BDT": "৳", "BGN": "лв", "BHD": "ب.د", "BIF": "Fr",
    # ...
    "UAH": "₴", "UGX": "Sh", "USD": "$", "UYU": "$", "UZS": "лв",
```

### Countries That No Longer Exist

The Geonames data includes countries that no longer exist. At this time, those countries are the Dutch Antilles (`AN`) and Serbia and Montenegro (`CS`). If you wish to import those countries, set the `CITIES_NO_LONGER_EXISTENT_COUNTRY_CODES` to an empty list (`[]`).

Default: `['CS', 'AN']`

```python
CITIES_NO_LONGER_EXISTENT_COUNTRY_CODES = ['CS', 'AN']
```

### Postal Code Validation

The Geonames data contains country postal code formats and regular expressions, as well as postal codes. Some of these postal codes do not match the regular expression of their country. Users who wish to ignore invalid postal codes when importing data can set the `CITIES_VALIDATE_POSTAL_CODES` setting to `True` to skip importing postal codes that do not validate the country postal code regular expression.

If you have regional knowledge of postal codes that do not validate, please either update the postal code itself or the country postal codes regular expression on the Geonames website. Doing this will help all Geonames users (including this project but also every other Geonames user).

```python
CITIES_VALIDATE_POSTAL_CODES = True
```

### Custom `slugify()` Function

You may wish to customize the slugs generated by django-cities. To do so, you will need to write your own `slugify()` function and specify its dotted import path in the `CITIES_SLUGIFY_FUNCTION`:

```python
CITIES_SLUGIFY_FUNCTION = 'cities.util.default_slugify'
```

Your customized slugify function should accept two arguments: the object itself and the slug generated by the object itself. It should return the final slug as a string.

Because the slugify function contains code that would be reused by multiple objects, there is only a single slugify function for all of the objects in django-cities. To generate different slugs for different types of objects, test against the object's class name (`obj.__class__.__name__`).

Default slugify function (see [`cities/util.py`](https://github.com/arthanson/django-cities-xtd/tree/master/cities/util.py#L35)):

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

### Cities Without Regions

Note: This used to be `CITIES_IGNORE_EMPTY_REGIONS`.

Some cities in the Geonames data files do not have region information. By default, these cities are imported as normal (they still have foreign keys to their country), but if you wish to *avoid* importing these cities, set `CITIES_SKIP_CITIES_WITH_EMPTY_REGIONS` to `True`:

```python
# Import cities without region (default False)
CITIES_SKIP_CITIES_WITH_EMPTY_REGIONS = True
```

### Languages/Locales To Import

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

### Limit Imported Postal Codes

Limit the imported postal codes to specific countries

Special value:

* `ALL` - import all postal codes

```python
CITIES_POSTAL_CODES = ['US', 'CA']
```

### Plugins

You can write your own plugins to process data before and after it is written to the database. See the section on [Writing Plugins](./writing-plugins.md) for details.

To activate plugins, you need to add their dotted import strings to the `CITIES_PLUGINS` option. This example activates the `postal_code_ca` and `reset_queries` plugins that come with django-cities:

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

## Import Data

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
