import sys

try:  # Python 3.4+
    from importlib import reload
except ImportError:
    try:  # Python 3.0 - 3.3
        from imp import reload
    except ImportError:
        # reload is a builtin in Python 2
        pass


from cities.conf import CONTINENT_DATA as DEFAULT_CONTINENT_DATA


def reload_continent_data(signal, sender, setting, value, enter):
    if setting != 'CITIES_CONTINENT_DATA':
        return

    if value is None:
        value = DEFAULT_CONTINENT_DATA

    # Force reload the conf value
    sys.modules['cities.conf'].CONTINENT_DATA = value
    sys.modules['cities.util'].CONTINENT_DATA = value


def reload_cities_settings(sender, setting, value, enter, **kwargs):
    if setting != 'CITIES_SKIP_CITIES_WITH_EMPTY_REGIONS':
        return

    reload(sys.modules['cities.conf'])
    reload(sys.modules['cities.management.commands.cities'])
