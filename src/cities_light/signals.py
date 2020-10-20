"""
Signals for this application.

.. py:data:: city_items_pre_import

    Emited by city_import() in the cities_light command for each row parsed in
    the data file. If a signal reciever raises InvalidItems then it will be
    skipped.

    An example is worth 1000 words: if you want to import only cities from
    France, USA and Belgium you could do as such::

        import cities_light

        def filter_city_import(sender, items, **kwargs):
            if items[8] not in ('FR', 'US', 'BE'):
                raise cities_light.InvalidItems()

        cities_light.signals.city_items_pre_import.connect(filter_city_import)

    Note: this signal gets a list rather than a City instance for performance
    reasons.

.. py:data:: region_items_pre_import

    Same as :py:data:`~cities_light.signals.city_items_pre_import`.

.. py:data:: country_items_pre_import

    Same as :py:data:`~cities_light.signals.region_items_pre_import` and
    :py:data:`cities_light.signals.city_items_pre_import`.

.. py:data:: translation_items_pre_import

    Same as :py:data:`~cities_light.signals.region_items_pre_import` and
    :py:data:`cities_light.signals.city_items_pre_import`.

    Note: Be careful because of long runtime; it will be called VERY often.

.. py:data:: city_items_post_import

    Emited by city_import() in the cities_light command for each row parsed in
    the data file, right before saving City object. Along with City instance
    it pass items with geonames data. Will be useful, if you define custom
    cities models with ``settings.CITIES_LIGHT_APP_NAME``.

    Example::

        import cities_light

        def process_city_import(sender, instance, items, **kwargs):
            instance.timezone = items[17]

        cities_light.signals.city_items_post_import.connect(process_city_import)

.. py:data:: region_items_post_import

    Same as :py:data:`~cities_light.signals.city_items_post_import`.

.. py:data:: country_items_post_import

    Same as :py:data:`~cities_light.signals.region_items_post_import` and
    :py:data:`cities_light.signals.city_items_post_import`.
"""
import django.dispatch

__all__ = [
    'country_items_pre_import', 'country_items_post_import',
    'region_items_pre_import', 'region_items_post_import',
    'subregion_items_pre_import', 'subregion_items_post_import',
    'city_items_pre_import', 'city_items_post_import',
    'translation_items_pre_import']

# providing_args=['items'] for signals below
city_items_pre_import = django.dispatch.Signal()
subregion_items_pre_import = django.dispatch.Signal()
region_items_pre_import = django.dispatch.Signal()
country_items_pre_import = django.dispatch.Signal()
translation_items_pre_import = django.dispatch.Signal()

# providing_args=['instance', 'items'] for all signals below
city_items_post_import = django.dispatch.Signal()
subregion_items_post_import = django.dispatch.Signal()
region_items_post_import = django.dispatch.Signal()
country_items_post_import = django.dispatch.Signal()
