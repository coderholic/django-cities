from django.db.models import signals
from .abstract_models import to_ascii, to_search
from .settings import *
from .signals import *
from .exceptions import *


def set_name_ascii(sender, instance=None, **kwargs):
    """
    Signal reciever that sets instance.name_ascii from instance.name.

    Ascii versions of names are often useful for autocompletes and search.
    """
    name_ascii = to_ascii(instance.name)

    if not name_ascii.strip():
        return

    if name_ascii and not instance.name_ascii:
        instance.name_ascii = to_ascii(instance.name)


def set_display_name(sender, instance=None, **kwargs):
    """
    Set instance.display_name to instance.get_display_name(), avoid spawning
    queries during __str__().
    """
    instance.display_name = instance.get_display_name()


def city_country(sender, instance, **kwargs):
    if instance.region_id and not instance.country_id:
        instance.country = instance.region.country


def city_search_names(sender, instance, **kwargs):
    search_names = []

    country_names = [instance.country.name]
    if instance.country.alternate_names:
        country_names += instance.country.alternate_names.split(',')

    city_names = [instance.name]
    if instance.alternate_names:
        city_names += instance.alternate_names.split(',')

    if instance.region_id:
        region_names = [instance.region.name]
        if instance.region.alternate_names:
            region_names += instance.region.alternate_names.split(',')

    for city_name in city_names:
        for country_name in country_names:
            name = to_search(city_name + country_name)
            if name not in search_names:
                search_names.append(name)

            if instance.region_id:
                for region_name in region_names:
                    name = to_search(city_name + region_name + country_name)
                    if name not in search_names:
                        search_names.append(name)

    instance.search_names = ' '.join(search_names)


def connect_default_signals(model_class):
    """
    Use this function to connect default signals to your custom model.
    It is called automatically, if default cities_light models are used,
    i.e. settings `CITIES_LIGHT_APP_NAME` is not changed.
    """
    if 'Country' in model_class.__name__:
        signals.pre_save.connect(set_name_ascii, sender=model_class)
    if 'Region' in model_class.__name__:
        signals.pre_save.connect(set_name_ascii, sender=model_class)
        signals.pre_save.connect(set_display_name, sender=model_class)
    if 'City' in model_class.__name__:
        signals.pre_save.connect(set_name_ascii, sender=model_class)
        signals.pre_save.connect(set_display_name, sender=model_class)
        signals.pre_save.connect(city_country, sender=model_class)
        signals.pre_save.connect(city_search_names, sender=model_class)


def filter_non_cities(sender, items, **kwargs):
    """
    Reports non populated places as invalid.
    By default, this reciever is connected to
    :py:func:`~cities_light.signals.city_items_pre_import`, it raises
    :py:class:`~cities_light.exceptions.InvalidItems` if the row doesn't have
    PPL in its features (it's not a populated place).
    """
    if 'PPL' not in items[7]:
        raise InvalidItems()
city_items_pre_import.connect(filter_non_cities)


def filter_non_included_countries_country(sender, items, **kwargs):
    """
    Exclude any **country** which country must not be included.
    This is slot is connected to the
    :py:func:`~cities_light.signals.country_items_pre_import` signal and does
    nothing by default.  To enable it, set the
    :py:data:`~cities_light.settings.INCLUDE_COUNTRIES` setting.
    """
    if INCLUDE_COUNTRIES is None:
        return

    if items[0].split('.')[0] not in INCLUDE_COUNTRIES:
        raise InvalidItems()
country_items_pre_import.connect(filter_non_included_countries_country)


def filter_non_included_countries_region(sender, items, **kwargs):
    """
    Exclude any **region** which country must not be included.
    This is slot is connected to the
    :py:func:`~cities_light.signals.region_items_pre_import` signal and does
    nothing by default.  To enable it, set the
    :py:data:`~cities_light.settings.INCLUDE_COUNTRIES` setting.
    """
    if INCLUDE_COUNTRIES is None:
        return

    if items[0].split('.')[0] not in INCLUDE_COUNTRIES:
        raise InvalidItems()
region_items_pre_import.connect(filter_non_included_countries_region)


def filter_non_included_countries_city(sender, items, **kwargs):
    """
    Exclude any **city** which country must not be included.
    This is slot is connected to the
    :py:func:`~cities_light.signals.city_items_pre_import` signal and does
    nothing by default.  To enable it, set the
    :py:data:`~cities_light.settings.INCLUDE_COUNTRIES` setting.
    """
    if INCLUDE_COUNTRIES is None:
        return

    if items[8].split('.')[0] not in INCLUDE_COUNTRIES:
        raise InvalidItems()
city_items_pre_import.connect(filter_non_included_countries_city)
