"""
By default, all models are taken from this package.
But it is possible to customise these models to add some fields.
For such purpose cities_light models are defined as abstract (without
customisation they all inherit abstract versions automatically
without changes).

Steps to customise cities_light models
======================================

- Define **all** of cities abstract models in your app:
    .. code:: python

        # yourapp/models.py

        from cities_light.abstract_models import (AbstractCity, AbstractRegion,
            AbstractCountry)
        from cities_light.receivers import connect_default_signals


        class Country(AbstractCountry):
            pass
        connect_default_signals(Country)

        class Region(AbstractRegion):
            pass
        connect_default_signals(Region)


        class City(AbstractCity):
            modification_date = models.CharField(max_length=40)
        connect_default_signals(City)

- Add post import processing to you model *[optional]*:
    .. code:: python

        import cities_light
        from cities_light.settings import ICity

        def set_city_fields(sender, instance, items, **kwargs):
            instance.modification_date = items[ICity.modificationDate]
        cities_light.signals.city_items_post_import.connect(set_city_fields)

- Define settings.py:
    .. code:: python

        INSTALLED_APPS = [
            # ...
            'cities_light',
            'yourapp',
        ]

        CITIES_LIGHT_APP_NAME = 'yourapp'

        # Disable built-in cities_light migrations
        MIGRATION_MODULES = {
            'cities_light': None
        }

- Create your own migrations:
    .. code::

        python manage.py makemigrations yourapp
        python manage.py migrate

That's all!

**Notes**:
    - model names can't be modified, i.e. you have to use exactly
      City, Country, Region names and not MyCity, MyCountry, MyRegion.
    - Connect default signals for every custom model by calling
      ``connect_default_signals`` (or not, if you don't want to trigger
      default signals).
    - if in further versions of cities_light abstract models will be
      updated (some fields will be added/removed), you have to deal with
      migrations by yourself, as models are on your own now.
"""

# some imports are present for backwards compatibility and migration process
from .abstract_models import (AbstractCountry, AbstractRegion, AbstractCity,
    ToSearchTextField, CONTINENT_CHOICES, to_search, to_ascii)
from .signals import *
from .receivers import *
from .settings import *

__all__ = ['CONTINENT_CHOICES', 'to_search', 'to_ascii', 'filter_non_cities',
    'filter_non_included_countries_country',
    'filter_non_included_countries_region',
    'filter_non_included_countries_city']

if CITIES_LIGHT_APP_NAME == DEFAULT_APP_NAME:
    class Country(AbstractCountry):
        pass
    connect_default_signals(Country)

    __all__.append('Country')

    class Region(AbstractRegion):
        pass
    connect_default_signals(Region)

    __all__.append('Region')

    class City(AbstractCity):
        pass
    connect_default_signals(City)

    __all__.append('City')
