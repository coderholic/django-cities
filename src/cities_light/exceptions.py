class CitiesLightException(Exception):
    """ Base exception class for this app's exceptions. """
    pass


class InvalidItems(CitiesLightException):
    """
    The cities_light command will skip item if a city_items_pre_import signal
    reciever raises this exception.
    """
    pass


class SourceFileDoesNotExist(CitiesLightException):
    """ A source file could not be found. """

    def __init__(self, source):
        super().__init__('%s does not exist' % source)
