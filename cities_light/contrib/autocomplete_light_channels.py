"""
Classes that couple autocomplete_light and cities_light.
"""

import autocomplete_light


class CityChannel(autocomplete_light.ChannelBase):
    """
    Sample City channel.
    """
    search_fields = ('search_names',)


class RegionChannel(autocomplete_light.ChannelBase):
    """
    Sample Region channel.
    """
    search_fields = ('name', 'name__ascii')


class CountryChannel(autocomplete_light.ChannelBase):
    """
    Sample Country channel.
    """
    search_field = ('name', 'name__ascii')
