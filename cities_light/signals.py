import django.dispatch

from exceptions import *

__all__ = ['city_items_pre_import']

city_items_pre_import = django.dispatch.Signal(providing_args=['items'])

def filter_non_cities(sender, items, **kwargs):
    if 'PPL' not in items[7]:
        raise InvalidItems()
city_items_pre_import.connect(filter_non_cities)
