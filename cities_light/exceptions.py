from __future__ import unicode_literals


class InvalidItems(Exception):
    """
    The cities_light command will skip item if a city_items_pre_import signal
    reciever raises this exception.
    """
    pass
