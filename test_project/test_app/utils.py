import sys

from cities.conf import CONTINENT_DATA as DEFAULT_CONTINENT_DATA


def reload_continent_data(signal, sender, setting, value, enter):
    if value is None:
        value = DEFAULT_CONTINENT_DATA

    # Force reload the conf value
    sys.modules['cities.conf'].CONTINENT_DATA = value
    sys.modules['cities.util'].CONTINENT_DATA = value
