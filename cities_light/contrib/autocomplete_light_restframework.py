"""
Channels that couple autocomplete_light and cities_light.
"""

import autocomplete_light

from ..models import Country, Region, City


class RemoteCitiesLightChannel(autocomplete_light.RemoteChannelBase):
    """
    Define model_for_source_url based on urls from
    cities_light.contrib.restframework.urlpatterns.
    """

    def model_for_source_url(self, url):
        """
        Return the appropriate model for the urls defined by
        cities_light.contrib.restframework.urlpatterns.

        Used by RemoteChannel.
        """
        if 'cities_light/city/' in url:
            return City
        elif 'cities_light/region/' in url:
            return Region
        elif 'cities_light/country/' in url:
            return Country


class RemoteCityChannel(RemoteCitiesLightChannel):
    """

    """
    search_fields = ('search_names',)


class RemoteRegionChannel(RemoteCitiesLightChannel):
    search_fields = ('name', 'name__ascii')


class RemoteCountryChannel(RemoteCitiesLightChannel):
    search_fields = ('name', 'name__ascii')
