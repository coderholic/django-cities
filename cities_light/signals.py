import django.dispatch

__all__ = ['city_items_pre_import']

city_items_pre_import = django.dispatch.Signal(providing_args=['items'])
